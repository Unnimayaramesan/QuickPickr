"""Lightweight ₹ parsing duplicated from query-service to keep indexer standalone."""

from __future__ import annotations

import re

INR_PATTERN = re.compile(r"₹\s?(\d+(?:[.,]\d{1,2})?)", re.IGNORECASE)


def extract_inr_anywhere(text: str) -> float | None:
    if not text:
        return None
    m = INR_PATTERN.search(text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None

