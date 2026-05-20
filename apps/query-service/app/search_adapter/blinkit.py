from __future__ import annotations

from typing import TYPE_CHECKING

from app.search_adapter import common as _adapter_common

if TYPE_CHECKING:
    from app.config import Settings


def search(
    query: str,
    settings: Settings,
    zone_id: str,
    *,
    page_size: int | None = None,
) -> list[dict]:
    return _adapter_common.search_filtered(query, settings, "blinkit", zone_id, page_size)
