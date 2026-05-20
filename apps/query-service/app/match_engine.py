"""Rules-based relevance: token overlap, pack hint, relevance score → confidence + suppress."""

from __future__ import annotations

import re
from typing import Any

_TOKEN = re.compile(r"[a-z0-9.%]+")


def normalize_query_tokens(q: str) -> list[str]:
    return [t for t in _TOKEN.findall(q.lower()) if len(t) > 1]


def token_overlap_ratio(query_tokens: list[str], title: str) -> float:
    if not query_tokens:
        return 0.0
    title_lower = title.lower()
    title_set = set(_TOKEN.findall(title_lower))
    if not title_set:
        return 0.0
    hits = sum(1 for t in query_tokens if t in title_set or t.rstrip(".") in title_set)
    return hits / max(len(query_tokens), 1)


def pack_hint_overlap(query_lower: str, pack_size: str) -> float:
    if not pack_size:
        return 0.25
    p = pack_size.lower().strip()
    if not p:
        return 0.25
    digits = "".join(ch for ch in p if ch.isdigit())
    if digits and digits in query_lower.replace(" ", ""):
        return 1.0
    # common volume tokens like 500 ml
    collapsed = "".join(query_lower.split())
    for token in (_TOKEN.findall(collapsed)):
        if len(token) >= 2 and token in p.replace(" ", ""):
            return 0.9
    return 0.4


def _brand_hint_score(query_tokens: list[str], title_lower: str) -> float:
    # Light heuristic: if first token appears in title (often brand-ish)
    if not query_tokens:
        return 0.25
    first = query_tokens[0]
    return 1.0 if first in title_lower else 0.35


def score_candidate(
    query: str,
    candidate: dict[str, Any],
    vertex_relevance: float | None,
) -> float:
    ql = query.lower().strip()
    q_tokens = normalize_query_tokens(query)
    title = str(candidate.get("title") or "")
    tl = title.lower()
    overlap = token_overlap_ratio(q_tokens, title)
    pack = pack_hint_overlap(ql, str(candidate.get("packSize") or ""))
    brand = _brand_hint_score(q_tokens, tl)

    rel = 0.4
    if vertex_relevance is not None:
        try:
            rel = float(vertex_relevance)
        except (TypeError, ValueError):
            rel = 0.4
    elif candidate.get("_vertex_rank") is not None:
        rk = candidate["_vertex_rank"]
        try:
            rel = max(0.0, min(1.0, 1.0 - float(rk) * 0.05))
        except (TypeError, ValueError):
            pass

    # Weighted composite in [0,1]
    return 0.45 * overlap + 0.2 * pack + 0.1 * brand + 0.25 * rel


def classify_match(score: float, low_threshold: float, suppress_threshold: float) -> tuple[str, bool]:
    """Returns (matchConfidence high|low, suppressed)."""
    if score < suppress_threshold:
        return "low", True
    if score < low_threshold:
        return "low", False
    return "high", False


def refine_hit(
    query: str,
    hit: dict[str, Any],
    settings: Any,
) -> dict[str, Any]:
    relevance = hit.get("vertexRelevanceScore")
    if relevance is None and hit.get("relevanceScore") is not None:
        relevance = hit.get("relevanceScore")

    raw_score = score_candidate(query, hit, relevance if relevance is None else float(relevance))
    conf, suppressed = classify_match(
        raw_score,
        settings.match_engine_low_threshold,
        settings.match_engine_suppress_threshold,
    )
    merged = dict(hit)
    merged["matchConfidence"] = conf
    merged["_match_score"] = raw_score
    merged["_suppress"] = suppressed
    return merged


def pick_best_for_retailer(query: str, hits: list[dict[str, Any]], settings: Any) -> dict[str, Any] | None:
    refined = [refine_hit(query, h, settings) for h in hits]
    kept = [h for h in refined if not h.get("_suppress")]
    pool = kept or refined

    priced = [h for h in pool if h.get("finalPriceInr") is not None]
    subset = priced or pool
    if not subset:
        return None

    subset.sort(key=lambda x: (-float(x.get("_match_score", 0.0)), x.get("finalPriceInr") or 1e12))
    best = subset[0]
    for k in ("_match_score", "_suppress", "_vertex_rank"):
        best.pop(k, None)
    return best
