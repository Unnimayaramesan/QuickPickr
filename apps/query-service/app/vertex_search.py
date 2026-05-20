"""Retailer enumeration / display map + legacy blended search helper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

RETAILER_DISPLAY: dict[str, str] = {
    "blinkit": "Blinkit",
    "zepto": "Zepto",
    "bigbasket": "BigBasket",
    "instamart": "Swiggy Instamart",
}

ALL_RETAILERS = tuple(RETAILER_DISPLAY.keys())

if TYPE_CHECKING:
    from app.config import Settings


def search_vertex(query: str, settings: Settings, page_size: int | None = None) -> list[dict[str, Any]]:
    """Blended Vertex search (backward compatible with verify_vertex + early scripts)."""
    from app.search_adapter.common import search_vertex_unfiltered

    return search_vertex_unfiltered(query, settings, page_size)


__all__ = ["ALL_RETAILERS", "RETAILER_DISPLAY", "search_vertex"]
