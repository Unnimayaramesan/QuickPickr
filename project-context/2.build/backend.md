# QuickPickr — Backend Epic Log

| Field | Value |
|-------|-------|
| **Author** | @backend.eng |
| **Plan** | [backend-plan.md](./backend-plan.md) |
| **Runtime** | FastAPI query service (`apps/query-service`) + Vertex AI Search (Discovery Engine) |
| **Status** | MVP query API implemented — golden-path AC depends on index + Vertex env |

---

## Summary

Delivered the **QuickPickr query service**:

- **FastAPI** app: `GET /health`, `POST /v1/search`, optional static dev UI under `/static`
- **Per-retailer** Vertex search (`blinkit`, `zepto`, `bigbasket`, `instamart`) with **strict** retailer filtering in `search_adapter` + `match_engine`
- **Pincode → zoneId** via `data/pincode_zones.json` + fallback (see SAD / backend-plan)
- **Cache** optional Redis (`REDIS_URL`); in-memory path when unset
- **Rate limit** per `X-Session-Id` (sliding window; configurable)
- **Config** via Pydantic Settings + repo-root `.env`; `load_dotenv` so ADC env vars work for Google clients
- **Boot without Vertex**: `vertex_search_serving_config` defaults empty; `/health` reports misconfiguration; search returns per-row `error`/`unavailable` when upstream fails

---

## Run locally

```powershell
# From repo root (sets PYTHONPATH)
npm run dev:api
# Or: see README `npm run dev` for web + API together

# Health / search (with API on :8080)
Invoke-RestMethod -Uri http://127.0.0.1:8080/health
```

Vertex setup: [backend-plan.md §1](./backend-plan.md#1-vertex-ai-search-discovery-engine--role-in-quickpickr).

---

## Key paths

| Area | Location |
|------|----------|
| App entry | `apps/query-service/app/main.py` |
| Search orchestration | `apps/query-service/app/search_service.py` |
| Vertex adapters | `apps/query-service/app/search_adapter/` |
| Match / refine | `apps/query-service/app/match_engine.py` |
| Settings | `apps/query-service/app/config.py` |

---

## Decisions

| Topic | Decision |
|-------|----------|
| Retrieval | Discovery Engine `SearchServiceClient`; serving config from env |
| Fan-out | Parallel per-retailer calls with timeouts + total budget |
| Non–QuickPickr retailers in index | Dropped in adapter + match engine (`ALL_RETAILERS` allowlist) |
| OpenAPI snapshot | `packages/api-contract/openapi.yaml` — export via `python scripts/export_openapi.py` when schema changes |

---

## Acceptance status (PRD tie-in)

| ID | Criterion | Status |
|----|-----------|--------|
| API shape | Four retailer rows + `meta` | Pass (see `npm run qa:api`) |
| AC-1 (≥3 available @ 560034) | Needs staging index + Vertex | Pending |
| AC-3 (P95 latency) | k6 / prod metrics | Pending |

---

## Known gaps / future work

- Full **OTLP** export to Cloud Trace / Monitoring (hooks exist; wiring deferred per backend-plan)
- **pytest** / golden Vertex fixtures under `apps/query-service/tests/` (planned in integration-plan §7)
- **Indexer** (`apps/indexer`) operational docs — separate from query-only MVP

---

## Audit

| Timestamp (UTC) | Persona | Action |
|-----------------|---------|--------|
| 2026-05-20T00:00:00Z | @backend.eng | Initial **backend.md** epic log (file was missing; plan + code existed) |
