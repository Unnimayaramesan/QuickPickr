# QuickPickr Indexer (Cloud Run Job)

Per-retailer crawlers ingest normalized SKU documents into the **single** Vertex AI Search data store. Run with:

```powershell
pip install -r requirements.txt

python -m indexer.main --retailer blinkit --tier warm --dry-run
```

Environment (repo-root `.env` recommended):

| Variable | Purpose |
|----------|---------|
| `VERTEX_DATA_STORE_BRANCH` | `$DATA_STORE_BRANCH` resource name ending in `/branch/default_branch` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local SA JSON |

## Three-tier refresh (SAD §5.3)

| Tier | Suggested Scheduler | Cron (IST) sketch |
|------|---------------------|-------------------|
| **hot** (2–5 min) | `*/4 * * * *` PDPs SKUs flagged `freshnessTier=hot` |
| **warm** (hourly) | `30 * * * *` bestsellers subset |
| **long-tail** (daily) | `15 4 * * *` remaining catalog shards |

Separate Cloud Scheduler jobs invoke the same Job image with `--tier hot|warm|long_tail`.

## Adapters contract

Each `adapters/*.py` module implements:

1. **`discover_urls(zone_id)`** → list of PDP URLs
2. **`parse_document(html)`** → dict `{ title, skuId, packSize, priceInr, productUrl, imageUrl, freshnessTier }`
3. **`rate_limit_policy()`** → `min_interval_seconds` respecting `robots.txt`

Imports use `VertexDocumentBuilder` helpers in `vertex_push.py`; production runs should enqueue batched **Import Documents** RPCs (avoid single-doc HTTP storm).
