from __future__ import annotations

from indexer.adapters import blinkit as _b


def discover_urls(zone_id: str, tier: str) -> list[str]:
    return _b.discover_urls(zone_id, tier)


def rate_limit_policy() -> dict[str, float]:
    return {"min_interval_seconds": 2.2}


def parse_document(html: str, absolute_url: str) -> dict:
    return _b.parse_document(html, absolute_url)
