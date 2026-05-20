# QuickPickr — Environment Setup (Vertex AI Search)

| Field | Value |
|-------|-------|
| **Date** | 2026-05-20 |
| **Author** | @project.mgr / @system.arch / @backend.eng |
| **Status** | Vertex search path documented |

---

## 1. Vertex AI Search credentials (quick setup)

Vertex AI Search is backed by the **Discovery Engine** API. QuickPickr only needs:

| Variable | Purpose |
|----------|---------|
| `VERTEX_SEARCH_SERVING_CONFIG` | Full resource name for `SearchRequest.serving_config` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to a **service account JSON key** (local dev); Cloud Run uses Workload Identity instead |

**Canonical backend notes:** step-by-step Console navigation, IAM roles, ADC behaviour, and troubleshooting live in **[backend-plan.md §1](./backend-plan.md#1-vertex-ai-search-discovery-engine--role-in-quickpickr)**.

### 1a. Example `.env` entries

```bash
VERTEX_SEARCH_SERVING_CONFIG=projects/958550029567/locations/global/collections/default_collection/engines/quickpickr_1778758368160/servingConfigs/default_search
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/you/.secrets/quickpickr-sa.json
```

Replace with **your** project number/id, engine id, and key path. Do **not** commit real paths or keys.

### 1b. Where each value comes from (summary)

**Serving config**

1. GCP Console → correct **project**.
2. **Vertex AI** → **Vertex AI Search** (or **Agent Builder / Gen App Builder** → your search app).
3. Open your **engine** → **Serving configs** → choose the config used for queries (often `default_search`).
4. Copy the **full resource name** (starts with `projects/…/servingConfigs/…`) into `VERTEX_SEARCH_SERVING_CONFIG`.

**Service account key**

1. **IAM & Admin** → **Service accounts** → create or select an SA.
2. Grant **`roles/discoveryengine.user`** at minimum for search; add **`roles/discoveryengine.editor`** (or narrower import roles) if you run the **indexer** from the same SA.
3. **Keys** → **Add key** → **JSON** → save outside git → set `GOOGLE_APPLICATION_CREDENTIALS` to that file path.

This repo loads `.env` with **`python-dotenv` into `os.environ`** (`apps/query-service/app/config.py`) so Google client libraries pick up `GOOGLE_APPLICATION_CREDENTIALS` correctly.

Your engine (`quickpickr_*` or equivalent) should index retailer catalog pages. The query service sends the **user product query** (plus optional filters) to this serving config and maps hits into four retailer rows.

---

## 2. Quick verify (CLI)

From the repository root:

```powershell
cd c:\Users\welcome\Documents\quick-pickr-project
python -m venv .venv
.\.venv\Scripts\activate
pip install -r apps\query-service\requirements.txt
python scripts\verify_vertex.py "Amul Gold 500 ml"
```

Expected: a list of indexed hits with titles and parsed ₹ prices.

---

## 3. Run the query API + web search UI

```powershell
cd apps\query-service
$env:PYTHONPATH = "."
uvicorn app.main:app --reload --port 8080
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8080/ | Dev search page (product + pincode) |
| http://127.0.0.1:8080/health | Vertex connectivity check |
| http://127.0.0.1:8080/docs | OpenAPI (Swagger) |

Example API call:

```powershell
curl -X POST http://127.0.0.1:8080/v1/search `
  -H "Content-Type: application/json" `
  -d '{"query":"Amul Gold 500 ml","pincode":"560034"}'
```

---

## 4. How search maps to QuickPickr

```mermaid
sequenceDiagram
  participant Web as Browser / Dev UI
  participant API as query-service
  participant V as Vertex AI Search

  Web->>API: POST /v1/search {query, pincode}
  API->>V: SearchRequest(serving_config, query)
  V-->>API: Documents + snippets
  API->>API: Parse ₹, group by retailer, rank
  API-->>Web: JSON table (4 rows)
```

**Pincode (v0):** Accepted and stored client-side; filtering by zone requires `zoneId` on indexed documents (see [sad.md](./sad.md) §5.3). Until zone facets exist, all hits come from the global index.

**Indexed fields (recommended):** `retailer`, `title`, `packSize`, `priceInr`, `productUrl`, `imageUrl`, `crawledAt` — improves row quality vs snippet-only parsing.

---

## 5. Troubleshooting

| Symptom | Check |
|---------|--------|
| `403` / `Permission denied` | Service account has **Discovery Engine User** (or Editor) on the project |
| `serving config not found` | Copy full path from GCP Console → AI Applications → your engine → serving config |
| Empty results | Data store indexed? Try a broad query (`milk`) in Console search preview |
| No ₹ in rows | Add `priceInr` to struct data at index time, or ensure snippets contain `₹` |

---

## Sources

- [sad.md](./sad.md) §5–§6
- [prd.md](../1.define/prd.md) §12 API contract
- Repo `apps/query-service/`

---

## Audit

| Timestamp (UTC) | Persona | Action |
|-----------------|---------|--------|
| 2026-05-19T20:00:00Z | @system.arch | Documented Vertex env vars and local query-service run path |
| 2026-05-20T12:00:00Z | @backend.eng | Linked backend-plan §1; expanded serving config + SA key steps |
