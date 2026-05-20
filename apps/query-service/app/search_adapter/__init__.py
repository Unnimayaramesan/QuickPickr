"""Per-retailer search adapters wrapping Vertex Discovery Engine."""

from __future__ import annotations

from app.config import Settings
from app.search_adapter.bigbasket import search as bb_search
from app.search_adapter.blinkit import search as bk_search
from app.search_adapter.instamart import search as ins_search
from app.search_adapter.zepto import search as zp_search
from app.vertex_search import ALL_RETAILERS

SEARCH_BY_RETAILER = {
    "blinkit": bk_search,
    "zepto": zp_search,
    "bigbasket": bb_search,
    "instamart": ins_search,
}


def search_sync(
    retailer_key: str,
    query: str,
    zone_id: str,
    settings: Settings,
) -> list[dict]:
    fn = SEARCH_BY_RETAILER[retailer_key]
    return fn(query, settings, zone_id)


__all__ = ["ALL_RETAILERS", "SEARCH_BY_RETAILER", "search_sync"]
