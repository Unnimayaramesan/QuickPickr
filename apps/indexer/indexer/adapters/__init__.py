from __future__ import annotations

from indexer.adapters import bigbasket, blinkit, instamart, zepto

ADAPTERS = {
    "blinkit": blinkit,
    "zepto": zepto,
    "bigbasket": bigbasket,
    "instamart": instamart,
}

__all__ = ["ADAPTERS"]
