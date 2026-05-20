from __future__ import annotations

# Stub: wire real URL discovery (sitemaps, internal search API) per SAD.


def discover_urls(zone_id: str, tier: str) -> list[str]:
    del zone_id, tier
    return []


def rate_limit_policy() -> dict[str, float]:
    return {"min_interval_seconds": 2.5}


def parse_document(html: str, absolute_url: str) -> dict:
    from indexer.adapters._html_utils import parse_open_graph
    from indexer.inr_parse import extract_inr_anywhere

    merged = parse_open_graph(html, absolute_url)
    snippet = merged.pop("_priceSnippet", "")
    pi = extract_inr_anywhere(snippet) or extract_inr_anywhere(html[:12000])
    merged["priceInr"] = pi
    return merged
