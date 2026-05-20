"""Shared Vertex Discovery Engine search primitives."""

from __future__ import annotations

import logging
from typing import Any

from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import GoogleAPICallError, InvalidArgument
from google.cloud import discoveryengine_v1 as discoveryengine

from app.config import Settings
from app.price_parser import extract_from_struct, parse_inr, struct_to_dict
from app.vertex_search import ALL_RETAILERS

_QP_RETAILERS = frozenset(ALL_RETAILERS)
_log = logging.getLogger(__name__)

# None = follow settings.vertex_use_schema_filters; False = facets rejected by Vertex.
_schema_filters_viable: bool | None = None


def _schema_filters_enabled(settings: Settings) -> bool:
    global _schema_filters_viable
    if _schema_filters_viable is False:
        return False
    if _schema_filters_viable is True:
        return True
    return settings.vertex_use_schema_filters


def _client() -> discoveryengine.SearchServiceClient:
    return discoveryengine.SearchServiceClient(
        client_options=ClientOptions(api_endpoint="discoveryengine.googleapis.com")
    )


def _document_fields(document: discoveryengine.Document) -> dict[str, Any]:
    struct = struct_to_dict(document.struct_data)
    derived = struct_to_dict(document.derived_struct_data)
    merged = {**derived, **struct}
    return extract_from_struct(merged)


def _snippet_text(result: discoveryengine.SearchResponse.SearchResult) -> str:
    if not result.document:
        return ""
    derived = struct_to_dict(result.document.derived_struct_data)
    snippets = derived.get("snippets")
    if snippets and len(snippets) > 0:
        first = snippets[0]
        if hasattr(first, "get"):
            return str(first.get("snippet", "") or "")
        if isinstance(first, dict):
            return str(first.get("snippet", ""))
        return str(first)
    return ""


def _filter_variants(retailer: str, zone_id: str, *, use_schema_filters: bool) -> list[str | None]:
    if not use_schema_filters:
        return [""]
    """Ordered filter chain — strict first, widen on empty."""
    escaped_retail = retailer.replace("\\", "").replace('"', "")
    escaped_zone = zone_id.replace("\\", "").replace('"', "")
    variants: list[str | None] = []
    if zone_id.strip():
        variants.append(f'retailer: ANY("{escaped_retail}") AND zoneId: ANY("{escaped_zone}")')
    variants.append(f'retailer: ANY("{escaped_retail}")')
    variants.append("")
    seen: set[str | None] = set()
    out: list[str | None] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def search_filtered(
    query: str,
    settings: Settings,
    retailer_key: str,
    zone_id: str,
    page_size: int | None,
) -> list[dict[str, Any]]:
    client = _client()
    ps = page_size or settings.vertex_page_size

    parsed: list[dict[str, Any]] = []
    last_exc: GoogleAPICallError | None = None
    any_variant_succeeded = False
    skip_to_unfiltered = False
    use_filters = _schema_filters_enabled(settings)

    for filt in _filter_variants(retailer_key, zone_id or "", use_schema_filters=use_filters):
        if skip_to_unfiltered and filt:
            continue
        filter_str = filt.strip() if filt else ""
        request = discoveryengine.SearchRequest(
            serving_config=settings.vertex_search_serving_config,
            query=query,
            page_size=ps,
            filter=filter_str,
        )

        try:
            search_iter = client.search(request).results
        except InvalidArgument as exc:
            _log.warning(
                "vertex_filter_rejected retailer=%s filter=%r query=%r msg=%s",
                retailer_key, filter_str or "<empty>", query, str(exc),
            )
            last_exc = exc
            if filter_str:
                global _schema_filters_viable
                _schema_filters_viable = False
                skip_to_unfiltered = True
            continue
        except GoogleAPICallError as exc:
            _log.warning(
                "vertex_call_failed retailer=%s filter=%r query=%r msg=%s",
                retailer_key, filter_str or "<empty>", query, str(exc),
            )
            last_exc = exc
            continue

        any_variant_succeeded = True

        ranked = 0
        for result in search_iter:
            if not result.document:
                continue
            fields = _document_fields(result.document)
            snippet = _snippet_text(result)
            fields["snippetForPriceFallback"] = snippet[:500]

            try:
                rel = getattr(result, "relevance_score", None)
                if rel is None and hasattr(result, "relevanceScore"):
                    rel = getattr(result, "relevanceScore")
                fields["vertexRelevanceScore"] = float(rel) if rel is not None else None
            except (TypeError, ValueError):
                fields["vertexRelevanceScore"] = None

            if fields.get("finalPriceInr") is None:
                fields["finalPriceInr"] = parse_inr(snippet) or parse_inr(fields.get("title") or "")
            if not fields.get("title") and snippet:
                fields["title"] = snippet[:120]

            guess = fields.get("retailer")
            if guess is not None:
                if guess not in _QP_RETAILERS:
                    continue
                if guess != retailer_key:
                    continue
            else:
                fields["retailer"] = retailer_key
            ranked += 1
            fields["_vertex_rank"] = ranked
            parsed.append(fields)

        if parsed:
            break

    if not any_variant_succeeded and last_exc is not None:
        raise last_exc

    return parsed


def probe_vertex(settings: Settings) -> None:
    """Single cheap search — validates auth + serving config (no structural filter)."""
    client = _client()
    req = discoveryengine.SearchRequest(
        serving_config=settings.vertex_search_serving_config,
        query="__qp_health__",
        page_size=1,
    )
    iter(client.search(req).results)


def search_vertex_unfiltered(query: str, settings: Settings, page_size: int | None = None) -> list[dict[str, Any]]:
    """Blended search (no retailer filter) — dev scripts / smoke tests."""
    client = _client()
    request = discoveryengine.SearchRequest(
        serving_config=settings.vertex_search_serving_config,
        query=query,
        page_size=page_size or settings.vertex_page_size,
    )
    parsed: list[dict[str, Any]] = []
    ranked = 0
    for result in client.search(request).results:
        if not result.document:
            continue
        fields = _document_fields(result.document)
        snippet = _snippet_text(result)
        fields["snippetForPriceFallback"] = snippet[:500]
        try:
            rel = getattr(result, "relevance_score", None)
            if rel is None and hasattr(result, "relevanceScore"):
                rel = getattr(result, "relevanceScore")
            fields["vertexRelevanceScore"] = float(rel) if rel is not None else None
        except (TypeError, ValueError):
            fields["vertexRelevanceScore"] = None
        if fields.get("finalPriceInr") is None:
            fields["finalPriceInr"] = parse_inr(snippet) or parse_inr(fields.get("title") or "")
        if not fields.get("title") and snippet:
            fields["title"] = snippet[:120]
        guess = fields.get("retailer")
        if guess not in _QP_RETAILERS:
            continue
        ranked += 1
        fields["_vertex_rank"] = ranked
        parsed.append(fields)
    return parsed
