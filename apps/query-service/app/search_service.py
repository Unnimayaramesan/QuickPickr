from __future__ import annotations

import time
from datetime import datetime, timezone

from app.config import Settings
from app.models import RowStatus, SearchMeta, SearchRequest, SearchResponse, SearchResultRow
from app.vertex_search import ALL_RETAILERS, RETAILER_DISPLAY, pick_best_per_retailer, search_vertex

# In-process cache for local dev (use Redis in production per SAD)
_CACHE: dict[str, tuple[float, SearchResponse]] = {}


def _cache_key(body: SearchRequest) -> str:
    q = " ".join(body.query.lower().split())
    return f"{q}|{body.pincode}"


def _build_rows(
    best_by_retailer: dict[str, dict | None],
    pincode: str,
) -> list[SearchResultRow]:
    rows: list[SearchResultRow] = []
    for retailer in ALL_RETAILERS:
        hit = best_by_retailer.get(retailer)
        display = RETAILER_DISPLAY[retailer]
        if not hit or not hit.get("finalPriceInr"):
            rows.append(
                SearchResultRow(
                    retailer=retailer,
                    retailerDisplayName=display,
                    status=RowStatus.unavailable,
                    message="Not available at your pincode",
                    matchConfidence="low",
                )
            )
            continue

        buy_url = hit.get("productUrl") or None
        rows.append(
            SearchResultRow(
                retailer=retailer,
                retailerDisplayName=display,
                title=hit.get("title") or "",
                packSize=hit.get("packSize") or "",
                imageUrl=hit.get("imageUrl") or "",
                finalPriceInr=hit.get("finalPriceInr"),
                matchConfidence=hit.get("matchConfidence", "high"),
                status=RowStatus.available,
                crawledAt=hit.get("crawledAt"),
                buyUrl=buy_url,
            )
        )

    rows.sort(
        key=lambda r: (r.finalPriceInr is None, r.finalPriceInr or float("inf")),
    )
    return rows


def run_search(body: SearchRequest, settings: Settings) -> SearchResponse:
    started = time.perf_counter()
    key = _cache_key(body)
    now = time.time()

    cached = _CACHE.get(key)
    if cached and (now - cached[0]) < settings.search_cache_ttl_seconds:
        response = cached[1].model_copy(deep=True)
        response.meta.cacheHit = True
        response.meta.latencyMs = int((time.perf_counter() - started) * 1000)
        return response

    try:
        hits = search_vertex(body.query, settings)
        best = pick_best_per_retailer(hits)
        rows = _build_rows(best, body.pincode)
    except Exception as exc:  # noqa: BLE001 — surface as error rows for MVP
        rows = [
            SearchResultRow(
                retailer=r,
                retailerDisplayName=RETAILER_DISPLAY[r],
                status=RowStatus.error,
                message=f"Temporarily unavailable ({type(exc).__name__})",
            )
            for r in ALL_RETAILERS
        ]

    latency_ms = int((time.perf_counter() - started) * 1000)
    response = SearchResponse(
        query=body.query,
        pincode=body.pincode,
        searchedAt=datetime.now(timezone.utc).isoformat(),
        results=rows,
        meta=SearchMeta(
            cacheHit=False,
            latencyMs=latency_ms,
            vertexServingConfig=settings.vertex_search_serving_config,
        ),
    )
    _CACHE[key] = (now, response.model_copy(deep=True))
    return response
