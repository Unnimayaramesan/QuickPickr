"""Resolve pincode → per-retailer zoneId (static overrides + deterministic fallback)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.vertex_search import ALL_RETAILERS

_ZONES_JSON = Path(__file__).resolve().parent.parent / "data" / "pincode_zones.json"


def _default_zone_id(pincode: str, retailer: str) -> str:
    """Stable zone key when DB has no override: IND-{pincode}-{retailer}."""
    return f"IND-{pincode}-{retailer}"


def _zones_table() -> dict[str, dict[str, str]]:
    if not _ZONES_JSON.exists():
        return {}
    try:
        raw = json.loads(_ZONES_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if isinstance(raw, dict):
        # Expected shape: { "560034": { "blinkit": "BLR-Z1", ... }, "prefix:560": { ... } }
        return raw  # type: ignore[return-value]
    return {}


@lru_cache(maxsize=1)
def zones_table_cached() -> dict[str, dict[str, str]]:
    return _zones_table()


def resolve_zones(pincode: str) -> dict[str, str]:
    """Return retailer → zoneId for this pincode."""
    table = zones_table_cached()
    key_exact = pincode
    prefix = pincode[:3]
    fallback_row = table.get(f"prefix:{prefix}") or table.get("__default_prefix__")

    zones: dict[str, str] = {}
    pin_row = table.get(key_exact)

    for r in ALL_RETAILERS:
        zone: str | None = None
        if pin_row and isinstance(pin_row.get(r), str):
            zone = pin_row[r]
        elif fallback_row and isinstance(fallback_row.get(r), str):
            zone = fallback_row[r]
        zones[r] = zone or _default_zone_id(pincode, r)

    return zones
