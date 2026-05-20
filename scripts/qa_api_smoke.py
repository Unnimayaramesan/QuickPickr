#!/usr/bin/env python3
"""
In-process API smoke checks for QuickPickr query-service (no running uvicorn).

Run from repo root:
  python scripts/qa_api_smoke.py

Optional:
  QA_RATE_LIMIT=1  — also verify 31st POST /v1/search returns 429 for same X-Session-Id
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QS = ROOT / "apps" / "query-service"


def _fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)
    sys.exit(1)


def main() -> None:
    sys.path.insert(0, str(QS))

    os.environ.setdefault(
        "VERTEX_SEARCH_SERVING_CONFIG",
        os.environ.get("VERTEX_SEARCH_SERVING_CONFIG") or "",
    )

    from fastapi.testclient import TestClient

    from app.main import app
    from app.vertex_search import ALL_RETAILERS

    # Context manager runs lifespan (rate limiter on app.state).
    with TestClient(app) as client:
        _run_checks(client, ALL_RETAILERS)


def _run_checks(client, ALL_RETAILERS: tuple[str, ...]) -> None:
    # GET /health
    h = client.get("/health")
    if h.status_code != 200:
        _fail(f"GET /health status {h.status_code}: {h.text[:300]}")
    health = h.json()
    for key in ("status", "vertexConfigured", "credentialsPathSet"):
        if key not in health:
            _fail(f"GET /health missing key {key}: {health}")

    # POST /v1/search — valid body (Vertex may be unconfigured; still 200 + 4 rows)
    sr = client.post(
        "/v1/search",
        json={"query": "Amul Gold 500 ml", "pincode": "560034"},
        headers={"X-Session-Id": "qa-smoke-session"},
    )
    if sr.status_code != 200:
        _fail(f"POST /v1/search status {sr.status_code}: {sr.text[:500]}")
    body = sr.json()
    if body.get("query") != "Amul Gold 500 ml" or body.get("pincode") != "560034":
        _fail(f"echo query/pincode mismatch: {body.get('query')} {body.get('pincode')}")
    results = body.get("results") or []
    if len(results) != len(ALL_RETAILERS):
        _fail(f"expected {len(ALL_RETAILERS)} retailer rows, got {len(results)}")
    retailers_got = {r.get("retailer") for r in results}
    if retailers_got != set(ALL_RETAILERS):
        _fail(f"retailer set mismatch: {retailers_got} vs {set(ALL_RETAILERS)}")
    for r in results:
        if "status" not in r or "retailerDisplayName" not in r:
            _fail(f"row missing fields: {json.dumps(r)[:200]}")
    meta = body.get("meta") or {}
    if "latencyMs" not in meta:
        _fail("meta.latencyMs missing")

    # Validation error (invalid pincode)
    bad = client.post(
        "/v1/search",
        json={"query": "Amul Gold", "pincode": "56003"},
        headers={"X-Session-Id": "qa-smoke-session-2"},
    )
    if bad.status_code not in (400, 422):
        _fail(f"invalid pincode expected 400/422, got {bad.status_code}")

    # Optional rate limit
    if os.environ.get("QA_RATE_LIMIT") == "1":
        sid = "qa-rate-limit-probe"
        last = None
        for i in range(31):
            last = client.post(
                "/v1/search",
                json={"query": f"qa rate limit probe {i}", "pincode": "110001"},
                headers={"X-Session-Id": sid},
            )
        if last is not None and last.status_code != 429:
            _fail(f"expected 429 on 31st request, got {last.status_code}: {last.text[:300]}")

    print("OK:", "GET /health,", "POST /v1/search (4 rows + meta), validation error")
    if os.environ.get("QA_RATE_LIMIT") == "1":
        print("OK:", "rate limit 429 on request 31")


if __name__ == "__main__":
    main()
