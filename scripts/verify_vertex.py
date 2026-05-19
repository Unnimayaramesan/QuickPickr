#!/usr/bin/env python3
"""Verify Vertex AI Search credentials and serving config from repo-root .env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "apps" / "query-service"))

from dotenv import load_dotenv

load_dotenv(_REPO / ".env")

serving = os.getenv("VERTEX_SEARCH_SERVING_CONFIG", "").strip()
creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()

if not serving:
    print("ERROR: VERTEX_SEARCH_SERVING_CONFIG is not set in .env")
    sys.exit(1)
if not creds:
    print("WARN: GOOGLE_APPLICATION_CREDENTIALS is not set (using ADC if available)")
elif not Path(creds).exists():
    print(f"ERROR: Credentials file not found: {creds}")
    sys.exit(1)

print(f"Serving config: {serving}")
print(f"Credentials:    {creds or '(application default)'}")

from app.config import get_settings
from app.vertex_search import search_vertex

settings = get_settings()
query = sys.argv[1] if len(sys.argv) > 1 else "Amul Gold 500 ml"
print(f"\nSearching for: {query!r}\n")

hits = search_vertex(query, settings, page_size=5)
if not hits:
    print("No results returned. Check that your data store is indexed.")
    sys.exit(0)

def _safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


for i, hit in enumerate(hits, 1):
    price = hit.get("finalPriceInr")
    title = _safe((hit.get("title") or "")[:60])
    print(f"{i}. [{hit.get('retailer') or '?'}] {title}")
    print(f"   INR {price}" if price else "   (no price parsed)")
    if hit.get("productUrl"):
        print(f"   {hit['productUrl'][:80]}")
    print()

print(f"OK — {len(hits)} hit(s) from Vertex AI Search")
