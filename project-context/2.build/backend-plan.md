# QuickPickr — Backend Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 1.2 |
| **Updated** | 2026-05-20 |
| **Author** | @backend.eng |
| **Inputs** | [prd.md](../1.define/prd.md), [mrd.md](../1.define/mrd.md), [sad.md](./sad.md) |

---

## 1. Vertex AI Search (Discovery Engine) — role in QuickPickr

QuickPickr uses **Vertex AI Search** (Google Cloud **Discovery Engine** API: `discoveryengine.googleapis.com`) as the retrieval layer over your indexed retailer catalog (structured documents and/or website crawl). The query service builds `SearchRequest` calls with:

- **`serving_config`** → full resource name from `VERTEX_SEARCH_SERVING_CONFIG`
- **`query`** → user product text
- **`filter`** (optional) → e.g. `retailer` + `zoneId` when those attributes exist on indexed documents

Indexed documents should expose fields aligned with [sad.md](./sad.md) §5.1 (`retailer`, `zoneId`, `skuId`, `title`, `packSize`, `priceInr`, `productUrl`, `imageUrl`, `crawledAt`, `freshnessTier`). Website-backed data stores often populate **derived** fields (`title`, `link`, `snippets`); the query service merges **struct + derived** data and falls back to ₹ regex where needed.

**Official references (bookmark these):**

- [Configure serving controls](https://cloud.google.com/generative-ai-app-builder/docs/configure-serving-controls) — serving configs tied to engines/data stores.
- [Discovery Engine Search API](https://cloud.google.com/python/docs/reference/discoveryengine/latest) — Python client (`google-cloud-discoveryengine`).

### 1.1 How to obtain `VERTEX_SEARCH_SERVING_CONFIG`

You need the **full resource name** of a **Serving Config** attached to your Search **Engine** (not just the engine ID). Typical shape:

```text
projects/PROJECT_ID_OR_NUMBER/locations/global/collections/default_collection/engines/ENGINE_ID/servingConfigs/SERVING_CONFIG_ID
```

Common defaults: collection `default_collection`, serving config id `default_search` — but **copy the exact string** from your project.

**Console path (labels may vary slightly by Google Cloud UI version):**

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select the correct **project**.
2. Navigate to **Vertex AI** → **Vertex AI Search** (or **Agent Builder / Gen App Builder** → your **app** / **data store**, depending on product entry point).
3. Open your **Search app / engine** (e.g. `quickpickr_*`).
4. Find **Serving configs** (or **Configurations** → **Serving**). Select the config you use for production or dev search (often `default_search`).
5. Copy the **full resource name** shown in the UI (or from the URL / “Resource name” field). Paste it **unchanged** into `VERTEX_SEARCH_SERVING_CONFIG`.

**CLI alternative (if you use gcloud with Discovery Engine APIs enabled):** list engines and serving configs under your data store collection, or read the resource name from a prior Terraform / export. The UI copy-paste path is usually fastest for MVP.

**Sanity check:** `GET /health` on the query service runs a one-document search against this `serving_config`; if the value is truncated or wrong, you will see `degraded` with an error message.

### 1.2 How to obtain `GOOGLE_APPLICATION_CREDENTIALS`

The **Discovery Engine client libraries** read **Application Default Credentials (ADC)**. For **local development**, the standard approach is a **service account JSON key file** whose path you set in `GOOGLE_APPLICATION_CREDENTIALS`.

**Why it exists alongside Pydantic Settings:** `pydantic-settings` loads `.env` into the `Settings` object, but **not** automatically into `os.environ`. This repo calls `load_dotenv()` in `apps/query-service/app/config.py` so `GOOGLE_APPLICATION_CREDENTIALS` is visible to Google’s libraries — keep the variable in `.env` and **never commit** the JSON file (use `.gitignore` for `.secrets/` and `.env`).

**Create or reuse a service account:**

1. **IAM & Admin** → **Service accounts** → **Create** (or pick an existing SA used for QuickPickr).
2. Grant roles minimally:
   - **Query path:** `roles/discoveryengine.user` (Discovery Engine User) is typically sufficient for **search** (`SearchServiceClient`).
   - **Indexer / import path:** additionally needs permission to **import documents** on the data store / branch (often `roles/discoveryengine.editor` or document-admin-style roles — confirm against your org policy).
3. **Keys** → **Add key** → **JSON** → download to a path **outside** git (e.g. `.secrets/quickpickr-sa.json`).
4. Set in `.env`:

   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/your-key.json
   ```

   Use absolute paths on Windows to avoid ambiguity.

**Production (Cloud Run / GKE):** Prefer **Workload Identity** — attach the same logical SA to the Cloud Run **service account** and **do not** bake JSON keys into the image. Omit `GOOGLE_APPLICATION_CREDENTIALS` in prod when ADC comes from the metadata server.

### 1.3 Prerequisites checklist

| Step | Action |
|------|--------|
| API | Enable **Discovery Engine API** (`discoveryengine.googleapis.com`) on the project |
| Billing | Billing enabled on the GCP project |
| Data | Data store populated (indexer or Console import); preview search in Console works |
| IAM | SA has Discovery Engine search (and import if indexing from CI/job) permissions |

More detailed local steps: [setup.md](./setup.md).

---

## 2. Architecture snapshot

| Workload | Goal |
|----------|------|
| **Query service** | Stateless FastAPI on Cloud Run: parallel Vertex Search ×4, SLO timeouts, Redis / memory cache, OTEL-ready metrics hooks, conservative logging |
| **Indexer** | Separate Cloud Run Job: httpx ingest + adapters + `import_documents` into one data store |

---

## 3. Query service checklist

### 3.1 Endpoints

| Item | Status | Notes |
|------|--------|-------|
| `POST /v1/search` | Done | `async`; `asyncio.gather(return_exceptions=False)` ×4 + outer `wait_for`; per-retailer `wait_for(..., asyncio.to_thread(...))`; `200`/`400`/`429` |
| `GET /health` | Done | Calls `probe_vertex()` (minimal unfiltered ping) |

### 3.2 Packages / modules (`apps/query-service/`)

| Module | Purpose | Status |
|--------|---------|--------|
| `app/config.py` | `python-dotenv` → `load_dotenv` before Settings; timeouts + tiers | Done |
| `app/search_adapter/*` | One module per retailer → shared `common.search_filtered()` | Done |
| `app/price_parser/*` | Struct merge + ₹ regex (`inr.py`), pack hints + `unitPriceLabel` (`normalize.py`) | Done |
| `app/match_engine.py` | Token / pack / relevance composite; suppress + `high`/`low` | Done |
| `app/pincode_resolver.py` | `data/pincode_zones.json` overrides + `IND-{pincode}-{retailer}` fallback | Done |
| `app/cache/` | SHA256 key, gzip JSON, Redis if `REDIS_URL` else memory; `asyncio.Lock` single-flight | Done |
| `app/rate_limit.py` | 30 req / 60s / `X-Session-Id` (default `anonymous-session`) | Done |
| `app/telemetry/metrics.py` | Counter hooks for required metric names (OTLP wiring later) | Done / partial |
| `app/logging_utils.py` | `pincode_prefix()` for structured logs | Done |
| `app/search_service.py` | Cache → parallel fan-out → row builder | Done |

### 3.3 Key decisions (audited)

| Topic | Choice |
|-------|--------|
| **Vertex + httpx** | Vertex uses sync gRPC client → parallelized with `asyncio.to_thread`. **httpx async** is used in the **indexer** for PDP fetches (per SAD request for async httpx on fetch paths). |
| **Per-retailer timeout** | `asyncio.wait_for(..., timeout=retailer_search_timeout_sec)` (default **800 ms** via `RETAILER_SEARCH_TIMEOUT_MS`). |
| **Global budget** | `asyncio.wait_for(gather(...), total_search_budget_sec)` default **2.8 s**; on breach → all rows `error` with “Temporarily unavailable”. |
| **Collect errors** | `gather(..., return_exceptions=False)` — individual retailers already return `error` rows; outer budget uses synthetic tuple list. |
| **Filter fallback** | `retailer+zoneId` → `retailer` only → unfiltered (compat with website index lacking facets). |
| **Final price vs fee** | `deliveryFeeInr` parsed when present; API row still exposes `finalPriceInr` from product list price (PRD alignment). |
| **OpenAPI** | Regenerate via `python scripts/export_openapi.py` → `packages/api-contract/openapi.yaml`. |

### 3.4 Open questions

| ID | Question | Proposed default |
|----|----------|------------------|
| B-1 | Discovery Engine filter attribute names differ per console setup? | Tune `retailer` / `zoneId` JSON keys in console; fallbacks already widen filters. |
| B-2 | Redis Memorystore URL format / TLS? | `REDIS_URL=rediss://...` when ready; dev leaves empty (in-memory). |
| B-3 | When **all** retailers hit outer 2.8 s budget? | Return four `error` rows (implemented). |

---

## 4. Indexer checklist (`apps/indexer/`)

| Item | Status | Notes |
|------|--------|-------|
| CLI `--retailer` `--tier` `--zone-id` `--dry-run` | Done | `python -m indexer` from `apps/indexer` + `PYTHONPATH=.` |
| Per-retailer adapter modules | Stub | `discover_urls` returns `[]` until real sitemap wiring |
| `parse_document` | Minimal | BeautifulSoup + OpenGraph + ₹ regex |
| `robots_helper.respectful_delay` | Done | Best-effort `robots.txt` crawl-delay |
| `vertex_push.publish_batch` | Done | `ImportDocuments` inline, `INCREMENTAL` reconciliation |
| Cloud Scheduler | Doc only | See [README](../../apps/indexer/README.md) |

---

## 5. Environment reference (`.env.example`)

See **§1** for how to obtain `VERTEX_SEARCH_SERVING_CONFIG` and `GOOGLE_APPLICATION_CREDENTIALS`. Other variables: optional `REDIS_URL`, `RETAILER_SEARCH_TIMEOUT_MS`, `TOTAL_SEARCH_BUDGET_SEC`, `VERTEX_DATA_STORE_BRANCH` (indexer).

---

## 6. Progress log

| When | What |
|------|------|
| 2026-05-20 | Query service modularized; async fan-out; cache; rate limit; telemetry hooks; indexer scaffold; OpenAPI export script |
| 2026-05-20 | Documented Vertex AI Search env: `VERTEX_SEARCH_SERVING_CONFIG` + `GOOGLE_APPLICATION_CREDENTIALS` |

---

## Sources

- Google Cloud — [Configure serving controls](https://cloud.google.com/generative-ai-app-builder/docs/configure-serving-controls)
- Google Cloud — [Discovery Engine Python client](https://cloud.google.com/python/docs/reference/discoveryengine/latest)
- [sad.md](./sad.md) §5 — Data store schema and indexing

---

## Assumptions

- GCP Console labels for Vertex AI Search / Agent Builder remain reachable under the Vertex AI product area.

---

## Open Questions

- Minimum IAM bindings for batch import if `discoveryengine.editor` is too broad for your org.

---

## Audit

| UTC | Persona | Action |
|-----|---------|--------|
| 2026-05-20 | @backend.eng | Created / refreshed backend plan + implementation pass |
| 2026-05-20 | @backend.eng | Expanded Vertex / GCP credential documentation |
