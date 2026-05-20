"""Price parsing facade (structured INR + ₹ regex + unit-price label helpers)."""

from __future__ import annotations

from app.price_parser.inr import parse_inr as parse_inr_text
from app.price_parser.normalize import format_unit_price_label, normalize_product_fields
from app.price_parser.struct_extract import extract_from_struct, infer_retailer, struct_to_dict

__all__ = [
    "infer_retailer",
    "extract_from_struct",
    "struct_to_dict",
    "parse_inr",
    "normalize_product_fields",
    "format_unit_price_label",
]


def parse_inr(text: str) -> float | None:
    """Public INR parser (backward compatible name)."""
    return parse_inr_text(text)
