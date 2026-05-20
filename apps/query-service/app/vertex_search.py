from __future__ import annotations

from typing import Any

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

from app.config import Settings
from app.price_parser import extract_from_struct, parse_inr, struct_to_dict

RETAILER_DISPLAY: dict[str, str] = {
    "blinkit": "Blinkit",
    "zepto": "Zepto",
    "bigbasket": "BigBasket",
    "instamart": "Swiggy Instamart",
}

ALL_RETAILERS = ("blinkit", "zepto", "bigbasket", "instamart")


def _client() -> discoveryengine.SearchServiceClient:
    return discoveryengine.SearchServiceClient(
        client_options=ClientOptions(api_endpoint="discoveryengine.googleapis.com")
    )


def _document_fields(document: discoveryengine.Document) -> dict[str, Any]:
    # Merge struct_data and derived_struct_data so we capture both structured
    # fields and Website-data-store fields (title, link, displayLink, etc.).
    struct = struct_to_dict(document.struct_data)
    derived = struct_to_dict(document.derived_struct_data)
    merged = {**derived, **struct}  # struct_data wins if both present
    return extract_from_struct(merged)


def _snippet_text(result: discoveryengine.SearchResponse.SearchResult) -> str:
    if not result.document:
        return ""
    derived = struct_to_dict(result.document.derived_struct_data)
    snippets = derived.get("snippets")
    if snippets and len(snippets) > 0:
        first = snippets[0]
        # Snippets may be proto MapComposite objects, not native dicts.
        if hasattr(first, "get"):
            return str(first.get("snippet", "") or "")
        if isinstance(first, dict):
            return str(first.get("snippet", ""))
        return str(first)
    return ""


def search_vertex(query: str, settings: Settings, page_size: int | None = None) -> list[dict[str, Any]]:
    """Run a single Vertex AI Search query against the configured serving config."""
    client = _client()
    request = discoveryengine.SearchRequest(
        serving_config=settings.vertex_search_serving_config,
        query=query,
        page_size=page_size or settings.vertex_page_size,
    )

    parsed: list[dict[str, Any]] = []
    response = client.search(request)

    for result in response.results:
        if not result.document:
            continue
        fields = _document_fields(result.document)
        snippet = _snippet_text(result)
        if fields.get("finalPriceInr") is None:
            fields["finalPriceInr"] = parse_inr(snippet)
        if not fields.get("title") and snippet:
            fields["title"] = snippet[:120]
        fields["matchConfidence"] = "high"
        fields["vertexRelevanceScore"] = getattr(result, "relevance_score", None)
        parsed.append(fields)

    return parsed


def pick_best_per_retailer(
    hits: list[dict[str, Any]],
) -> dict[str, dict[str, Any] | None]:
    """Keep the lowest-price hit per retailer (when retailer is known)."""
    buckets: dict[str, list[dict[str, Any]]] = {r: [] for r in ALL_RETAILERS}
    unknown: list[dict[str, Any]] = []

    for hit in hits:
        retailer = hit.get("retailer")
        if retailer in buckets:
            buckets[retailer].append(hit)
        else:
            unknown.append(hit)

    best: dict[str, dict[str, Any] | None] = {}
    for retailer, items in buckets.items():
        priced = [i for i in items if i.get("finalPriceInr") is not None]
        if priced:
            best[retailer] = min(priced, key=lambda x: x["finalPriceInr"])
        elif items:
            best[retailer] = items[0]
        else:
            best[retailer] = None

    # Distribute unknown hits to empty slots if any
    for hit in unknown:
        for retailer in ALL_RETAILERS:
            if best[retailer] is None:
                hit = {**hit, "retailer": retailer}
                best[retailer] = hit
                break

    return best
