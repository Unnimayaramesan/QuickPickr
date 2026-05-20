"""Cache backend: Redis (optional) / in-memory fallback; asyncio lock avoids stampedes."""

from __future__ import annotations

import asyncio
import gzip
import json
import os
from collections import defaultdict
from hashlib import sha256
from time import monotonic as mono
from typing import Any, Awaitable, Callable, NamedTuple


class CachedPayload(NamedTuple):
    expires_at_mono: float
    value: dict[str, Any]


_SF_LOCKS: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
_M_CACHE: dict[str, CachedPayload] = {}


def _normalize_cache_digest(norm_query: str, pincode: str) -> str:
    raw = f"{norm_query}|{pincode}".encode("utf-8")
    return sha256(raw).hexdigest()


def _redis_url() -> str | None:
    return (
        os.environ.get("REDIS_URL")
        or os.environ.get("REDIS_CLOUD_URL")  # some teams use alternate name
        or None
    )


def _compress_json(obj: dict[str, Any]) -> bytes:
    return gzip.compress(json.dumps(obj).encode("utf-8"))


def _decompress_json(buf: bytes) -> dict[str, Any]:
    return json.loads(gzip.decompress(buf).decode("utf-8"))


async def _redis_get_blob(key: str) -> bytes | None:
    try:
        import redis.asyncio as aioredis  # type: ignore[import-not-found]
    except ImportError:
        return None
    url = _redis_url()
    if not url:
        return None
    client = aioredis.from_url(url)
    try:
        return await client.get(key)
    finally:
        await client.close()


async def _redis_set_blob(key: str, ttl_sec: int, blob: bytes) -> None:
    try:
        import redis.asyncio as aioredis  # type: ignore[import-not-found]
    except ImportError:
        return
    url = _redis_url()
    if not url:
        return
    client = aioredis.from_url(url)
    try:
        await client.setex(key, ttl_sec, blob)
    finally:
        await client.close()


async def cache_get_json(key: str) -> dict[str, Any] | None:
    rcli_hit = await _redis_get_blob(key)
    if rcli_hit:
        try:
            return _decompress_json(rcli_hit)
        except Exception:
            return None

    row = _M_CACHE.get(key)
    if not row:
        return None
    if mono() >= row.expires_at_mono:
        _M_CACHE.pop(key, None)
        return None
    return row.value.copy()


async def cache_set_json(key: str, ttl_sec: int, value: dict[str, Any]) -> None:
    if _redis_url():
        await _redis_set_blob(key, ttl_sec, _compress_json(value))
    _M_CACHE[key] = CachedPayload(expires_at_mono=mono() + float(ttl_sec), value=value.copy())


async def get_or_compute(
    namespace: str,
    norm_query: str,
    pincode: str,
    ttl_seconds: int,
    compute_async: Callable[[], Awaitable[dict[str, Any]]],
    ttl_for_value: Callable[[dict[str, Any]], int] | None = None,
) -> tuple[dict[str, Any], bool]:
    """Singleflight-protected cached compute.

    `ttl_for_value` (optional) lets the caller pick the TTL based on the computed
    payload — return a positive int to cache for that many seconds, or 0/negative
    to skip the cache write entirely. When omitted, `ttl_seconds` is used for
    every payload (legacy behaviour).
    """
    digest = _normalize_cache_digest(norm_query, pincode)
    full_key = f"{namespace}{digest}"

    lk = _SF_LOCKS[f"{namespace}:{digest}"]
    async with lk:
        cached = await cache_get_json(full_key)
        if cached is not None:
            merged = cached.copy()
            meta = merged.get("meta") or {}
            meta["cacheHit"] = True
            merged["meta"] = meta
            return merged, True

        computed = await compute_async()
        merged = computed.copy()
        meta = merged.get("meta") or {}
        meta["cacheHit"] = False
        merged["meta"] = meta

        effective_ttl = ttl_seconds if ttl_for_value is None else ttl_for_value(merged)
        if effective_ttl > 0:
            await cache_set_json(full_key, effective_ttl, merged)
        return merged, False
