"""Vertex AI Search — batch import helpers."""

from __future__ import annotations

import logging
from typing import Any

from google.cloud import discoveryengine_v1 as discoveryengine

LOG = logging.getLogger("quickpickr.indexer.vertex")


def build_document(struct_fields: dict[str, Any]) -> discoveryengine.Document:
    sku = str(struct_fields.get("skuId") or struct_fields.get("productUrl") or "")[:240]
    doc_id_raw = f"{struct_fields['retailer']}|{struct_fields['zoneId']}|{sku}"
    doc_id = doc_id_raw.replace("/", "_")[:240]

    normalized = dict(struct_fields)
    pi = normalized.get("priceInr")
    if pi is not None:
        try:
            normalized["priceInr"] = float(pi)
        except (TypeError, ValueError):
            normalized["priceInr"] = 0.0

    return discoveryengine.Document(id=doc_id, struct_data=normalized)


def publish_batch(parent_branch: str, documents: list[discoveryengine.Document]) -> None:
    if not documents:
        return
    client = discoveryengine.DocumentServiceClient()
    op = client.import_documents(
        discoveryengine.ImportDocumentsRequest(
            parent=parent_branch,
            reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
            inline_source=discoveryengine.ImportDocumentsRequest.InlineSource(documents=documents),
        ),
    )
    LOG.info("import_documents LRO started shard_size=%s", len(documents))
    op.result(timeout=600)
    LOG.info("import_documents LRO completed")


__all__ = ["build_document", "publish_batch"]
