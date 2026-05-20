"""Async orchestration for /v1/search — parallel per-retailer Vertex + cache + telemetry."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from app.cache import get_or_compute
from app.config import Settings
from app.logging_utils import pincode_prefix
from app.match_engine import pick_best_for_retailer
from app.models import RowStatus, SearchMeta, SearchRequest, SearchResponse, SearchResultRow
from app.pincode_resolver import resolve_zones
from app.price_parser import normalize_product_fields
from app.search_adapter import search_sync
from app.telemetry.metrics import (
    record_cache_hit,
    record_freshness_age_minutes,
    record_parse_failure,
    record_retailer_timeout,
    record_search_latency_ms,
    record_zero_result_city,
)
from app.vertex_search import ALL_RETAILERS, RETAILER_DISPLAY

_log = logging.getLogger(__name__)


def _norm_query(body: SearchRequest) -> str:
    return " ".join(body.query.lower().split())


def _freshness_minutes(hit: dict[str, Any]) -> float | None:
    ca = hit.get("crawledAt")
    if not ca:
        return None
    try:
        s = str(ca).strip()
        if s.endswith("Z") and "+" not in s:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(s)
        delta = datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
        return max(0.0, delta.total_seconds() / 60.0)
    except Exception:
        return None


def _hits_to_best(query: str, hits: list[dict[str, Any]], settings: Settings) -> dict[str, Any] | None:
    best = pick_best_for_retailer(query, hits, settings)
    if not best:
        return None
    return normalize_product_fields(best)


def _retailer_row_available(hit: dict[str, Any], retailer: str) -> SearchResultRow:
    buy_url = hit.get("productUrl") or None
    return SearchResultRow(
        retailer=retailer,
        retailerDisplayName=RETAILER_DISPLAY[retailer],
        title=hit.get("title") or "",
        packSize=str(hit.get("packSize") or ""),
        imageUrl=str(hit.get("imageUrl") or ""),
        finalPriceInr=hit.get("finalPriceInr"),
        unitPriceLabel=hit.get("unitPriceLabel"),
        matchConfidence=hit.get("matchConfidence") or "high",
        status=RowStatus.available,
        crawledAt=hit.get("crawledAt"),
        buyUrl=buy_url,
    )


async def _fan_out_per_retailer(
    body: SearchRequest,
    settings: Settings,
    zones: dict[str, str],
) -> tuple[list[SearchResultRow], int]:
    """Returns (ordered rows, priced_hit_count_after_sort)."""

    async def call_one(retailer: str):
        tout = settings.retailer_search_timeout_sec
        zone_id = zones[retailer]
        error: str | None = None
        raw_hits: list[dict[str, Any]] | None = None
        try:
            raw_hits = await asyncio.wait_for(
                asyncio.to_thread(search_sync, retailer, body.query.strip(), zone_id, settings),
                timeout=tout,
            )
            return retailer, raw_hits, None
        except asyncio.TimeoutError:
            record_retailer_timeout(retailer)
            error = "timeout"
        except Exception:
            record_parse_failure(retailer)
            _log.warning("vertex_retailer_error", extra={"retailer": retailer}, exc_info=True)
            error = "exception"

        return retailer, None, error

    gatherable = asyncio.gather(*[call_one(r) for r in ALL_RETAILERS], return_exceptions=False)
    try:
        raw_results = await asyncio.wait_for(gatherable, timeout=settings.total_search_budget_sec)
    except asyncio.TimeoutError:
        raw_results = [(r, None, "budget_time") for r in ALL_RETAILERS]

    rows: list[SearchResultRow] = []
    priced_any = 0

    for retailer, hits, error in raw_results:
        display = RETAILER_DISPLAY[retailer]

        if error in {"timeout", "budget_time"}:
            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    status=RowStatus.error,
                    message="Temporarily unavailable",
                    matchConfidence="low",
                )
            )
            continue

        if error == "exception":
            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    status=RowStatus.error,
                    message="Temporarily unavailable",
                    matchConfidence="low",
                )
            )
            continue

        if not hits:
            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    status=RowStatus.unavailable,
                    message="Not available at your pincode",
                    matchConfidence="low",
                )
            )
            continue

        best = _hits_to_best(body.query, hits, settings)
        if best is None:
            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    status=RowStatus.unavailable,
                    message="No confident match — try refining your query",
                    matchConfidence="low",
                )
            )
            continue

        if best.get("finalPriceInr") is None:
            fm = _freshness_minutes(best)
            if fm is not None:
                record_freshness_age_minutes(fm)

            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    title=best.get("title") or "",
                    packSize=str(best.get("packSize") or ""),
                    status=RowStatus.unavailable,
                    message="Matched product but price not parsed — check retailer",
                    matchConfidence=best.get("matchConfidence") or "low",
                )
            )
            record_parse_failure(retailer)
            continue

        fm = _freshness_minutes(best)
        if fm is not None:
            record_freshness_age_minutes(fm)

        rows.append(_retailer_row_available(best, retailer))
        priced_any += 1

    rows.sort(key=lambda rr: (rr.finalPriceInr is None, rr.finalPriceInr or float("inf")))

    if priced_any == 0:
        record_zero_result_city(pincode_prefix(body.pincode))

    return rows, priced_any


async def _compute_response(body: SearchRequest, settings: Settings) -> dict[str, Any]:
    started = time.perf_counter()
    zones = resolve_zones(body.pincode)
    rows, _ = await _fan_out_per_retailer(body, settings, zones)
    latency_ms = int((time.perf_counter() - started) * 1000)
    record_search_latency_ms(latency_ms)

    response = SearchResponse(
        query=body.query,
        pincode=body.pincode,
        searchedAt=datetime.now(timezone.utc).isoformat(),
        results=rows,
        meta=SearchMeta(
            cacheHit=False,
            latencyMs=latency_ms,
            vertexServingConfig=settings.vertex_search_serving_config,
        ),
    )

    payload = json.loads(response.model_dump_json())
    payload["meta"]["cacheHit"] = False
    return payload


def _choose_cache_ttl(payload: dict[str, Any], settings: Settings) -> int:
    """Pick a per-payload TTL.

    All-error responses (every retailer row in status=error) get the short
    `negative_cache_ttl_seconds` so a transient Vertex/retailer failure cannot
    poison the cache for the full success TTL. Mixed and all-success responses
    keep the configured `search_cache_ttl_seconds`. A retailer that returned
    `status=unavailable` (a real "no products at this pincode" signal from the
    adapter) is treated as a valid answer and does NOT count as an error.
    """
    results = payload.get("results") or []
    if not results:
        # No rows at all is itself a degraded response — treat like an error.
        return settings.negative_cache_ttl_seconds
    statuses = {r.get("status") for r in results if isinstance(r, dict)}
    if statuses and statuses.issubset({"error"}):
        return settings.negative_cache_ttl_seconds
    return settings.search_cache_ttl_seconds


async def run_search_cached(body: SearchRequest, settings: Settings) -> SearchResponse:
    nq = _norm_query(body)
    prefix_label = pincode_prefix(body.pincode)
    _log.info("search_start", extra={"pincode_prefix": prefix_label, "q_len": len(body.query.strip())})

    async def compute() -> dict[str, Any]:
        payload = await _compute_response(body, settings)
        return payload

    payload, cached = await get_or_compute(
        "qp:search:v1:",
        nq,
        body.pincode,
        settings.search_cache_ttl_seconds,
        compute,
        ttl_for_value=lambda v: _choose_cache_ttl(v, settings),
    )
    record_cache_hit(cached)

    latency_for_log = payload.get("meta", {}).get("latencyMs") or 0
    retailer_hits = sum(
        1 for r in payload.get("results", []) if isinstance(r, dict) and r.get("status") == "available"
    )
    _log.info(
        "search_done",
        extra={
            "pincode_prefix": prefix_label,
            "latency_ms": latency_for_log,
            "cache_hit": cached,
            "retailer_hits": retailer_hits,
        },
    )

    return SearchResponse.model_validate(payload)
