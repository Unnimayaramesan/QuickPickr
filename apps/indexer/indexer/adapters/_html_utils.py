"""Shared PDP HTML helpers (minimal; extend per-retailer parsers)."""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup


def parse_open_graph(html: str, fallback_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    og = lambda prop: soup.find("meta", property=f"og:{prop}")  # noqa: E731 — tiny helper

    def content(tag) -> str:
        return (tag.get("content") if tag else "") or ""

    title = content(og("title")) or (soup.title.string.strip() if soup.title and soup.title.string else "")
    image = content(og("image"))
    price_raw = ""

    cand = soup.find(string=lambda s: isinstance(s, str) and "₹" in s)
    if cand:
        price_raw = str(cand).strip()[:120]

    return {
        "title": title.strip()[:300],
        "packSize": "",
        "skuId": "",
        "priceInr": None,
        "imageUrl": image.strip(),
        "productUrl": fallback_url,
        "_priceSnippet": price_raw,
    }


__all__ = ["parse_open_graph"]
