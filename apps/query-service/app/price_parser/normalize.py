"""Unit price label (₹ per ml/l/g/kg) derived from parsed pack hints."""

from __future__ import annotations

import re
from typing import Any

VolumeRe = re.compile(
    r"([\d.]+\s*(?:ml|mL|ML|liter|ltr|ltrs|ltr\.|l|L|gm|Gm|GM|g|G|kg|KG|Kg))\b",
)


def extract_quantity_ml_g(text: str) -> tuple[float, str] | None:
    if not text:
        return None
    m = VolumeRe.search(text.replace(",", "").lower())
    if not m:
        return None
    raw = m.group(1).lower().strip()
    num_match = re.match(r"([\d.]+)", raw)
    if not num_match:
        return None
    try:
        n = float(num_match.group(1))
    except ValueError:
        return None
    if "kg" in raw:
        return n * 1000.0, "g"
    if raw.endswith(" l") or "liter" in raw or raw.endswith("ltr") or (raw.endswith("l") and "ml" not in raw):
        return n * 1000.0, "ml"
    if "ml" in raw:
        return n, "ml"
    if "g" in raw or "gm" in raw:
        return n, "g"
    return None


def format_unit_price_label(final_price_inr: float | None, pack_size: str, title: str) -> str | None:
    if final_price_inr is None:
        return None
    qty = extract_quantity_ml_g(pack_size) or extract_quantity_ml_g(title)
    if not qty:
        return None
    amount, dim = qty
    if amount <= 0:
        return None
    per = final_price_inr / amount
    if dim == "ml":
        if amount >= 1000:
            return f"₹{per * 1000:.2f}/L approx."
        return f"₹{per:.4f}/ml approx."
    if dim == "g":
        if amount >= 1000:
            return f"₹{per * 1000:.2f}/kg approx."
        return f"₹{per:.4f}/g approx."
    return None


def normalize_product_fields(hit: dict[str, Any]) -> dict[str, Any]:
    merged = dict(hit)
    merged["unitPriceLabel"] = format_unit_price_label(
        merged.get("finalPriceInr"),
        str(merged.get("packSize") or ""),
        str(merged.get("title") or ""),
    )
    return merged
