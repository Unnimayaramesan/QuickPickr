"""INR extraction from snippets and localized patterns."""

from __future__ import annotations

import re

INR_PATTERN = re.compile(r"₹\s?(\d+(?:[.,]\d{1,2})?)", re.IGNORECASE)
ALT_INR_PATTERN = re.compile(r"Rs\.?\s?(\d+(?:[.,]\d{1,2})?)", re.IGNORECASE)


def parse_inr(text: str) -> float | None:
    if not text:
        return None
    for pattern in (INR_PATTERN, ALT_INR_PATTERN):
        match = pattern.search(text)
        if match:
            raw = match.group(1).replace(",", "")
            try:
                # Indian-style 1.199 might mean 1199 rare - keep float as-is for rupees.xx
                return float(raw)
            except ValueError:
                continue
    return None
