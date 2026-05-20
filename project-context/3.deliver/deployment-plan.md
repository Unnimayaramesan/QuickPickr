# QuickPickr — Deployment Plan

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Updated** | 2026-05-21 |
| **Author** | DevOps / Phase 3 Deliver |
| **Inputs** | [prd.md](../1.define/prd.md), [sad.md](../2.build/sad.md), [architecture-plan.md](../2.build/architecture-plan.md), [backend-plan.md](../2.build/backend-plan.md), [integration-plan.md](../2.build/integration-plan.md), [setup.md](../2.build/setup.md) |

---

## 1. Deployment approach

QuickPickr uses **three tiers** aligned with [SAD §9](../2.build/sad.md#9-deployment-view):

| Tier | Use case | Components | Status |
|------|----------|------------|--------|
| **A — Local (native)** | Day-to-day dev | `npm run dev` (Next.js + uvicorn) | **Available** — [setup.md](../2.build/setup.md), README |
| **B — Local (Docker Compose)** | Parity testing, onboarding, CI-like stack | `api` + `web` + `redis` | **Available** — `docker-compose.yml` |
| **C — Cloud (GCP)** | Staging / production | Cloud Run (query-service), Cloud Run Jobs (indexer), Vertex AI Search, Memorystore Redis; web on **Vercel** or **Cloud Run** | **Documented** — example scripts; infra provisioning manual |

**Recommended path:** **A** for development → **B** before release candidates → **C** for staging/prod with separate Vertex data stores per environment ([architecture-plan §6.2](../2.build/architecture-plan.md#61-required-secrets-expand-envexample)).

Mobile (Expo) is distributed via **EAS / store builds** pointing `EXPO_PUBLIC_API_URL` at the deployed API URL (not containerized in this repo’s compose file).

---

## 2. Required dependencies and environment setup

### 2.1 Tools

| Tool | Local native | Docker Compose | Cloud (GCP) |
|------|--------------|----------------|-------------|
| Node.js 18+ | Yes | In web image | Cloud Build / Vercel |
| Python 3.11+ | Yes | In api image | Cloud Run runtime |
| Docker 24+ | Optional | Yes | Artifact Registry |
| gcloud CLI | Optional | Optional | Yes |
| Vertex AI Search API enabled | Yes | Yes | Yes |

### 2.2 GCP prerequisites (staging / prod)

| Step | Action |
|------|--------|
| 1 | Enable `discoveryengine.googleapis.com` on the project |
| 2 | Create Vertex data store + serving config ([backend-plan §1](../2.build/backend-plan.md#1-vertex-ai-search-discovery-engine--role-in-quickpickr)) |
| 3 | Service account: `roles/discoveryengine.user` (query); import role for indexer |
| 4 | Secret Manager: `VERTEX_SEARCH_SERVING_CONFIG`, optional `REDIS_URL` |
| 5 | Memorystore Redis (prod) or omit (in-memory cache per instance — not recommended multi-instance) |
| 6 | Artifact Registry repository `quickpickr` |

### 2.3 Install (fresh clone)

```powershell
npm install --include=optional
pip install -r apps\query-service\requirements.txt
copy .env.example .env
# Fill VERTEX_SEARCH_SERVING_CONFIG, GOOGLE_APPLICATION_CREDENTIALS (local)
```

---

## 3. Configuration requirements

### 3.1 Environment matrix

| Variable | Local native | Docker Compose | Cloud Run (API) |
|----------|--------------|----------------|-----------------|
| `VERTEX_SEARCH_SERVING_CONFIG` | Required | Required | Secret Manager |
| `GOOGLE_APPLICATION_CREDENTIALS` | SA JSON path | Use `docker-compose.gcp.yml` mount | **Workload Identity** (no JSON) |
| `REDIS_URL` | Optional | `redis://redis:6379/0` | Memorystore URL |
| `CORS_ORIGINS` | localhost:3000 | Same + published web URL | Prod web origin(s) |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8080` | **`http://127.0.0.1:8080`** (browser on host) | `https://query-….run.app` |
| `ENABLE_RATE_LIMIT` | `true` | `true` | `true` |
| `ENVIRONMENT` | `dev` | `staging` | `prod` |

Templates: repo-root [`.env.example`](../../.env.example), [`.env.docker.example`](../../.env.docker.example).

### 3.2 Web build-time API URL

`NEXT_PUBLIC_API_URL` is **baked at Next.js build**. For Docker web image, build arg defaults to `http://127.0.0.1:8080`. For production, rebuild web with:

```bash
docker build -f apps/web/Dockerfile --build-arg NEXT_PUBLIC_API_URL=https://YOUR-API-URL .
```

Or set on Vercel / Cloud Run build environment.

### 3.3 Security

- Never commit `.env`, `.secrets/`, or SA JSON.
- Do **not** add blanket `*.json` to `.gitignore` (breaks tracked config) — see [qa-plan ISS-QA-001](../2.build/qa-plan.md#6-issues-found).
- Pincode must not appear in full in logs (SAD §8.3) — verify after deploy.

---

## 4. Deployment steps

### 4.1 Tier A — Local native (default)

```powershell
npm run dev
# Web http://localhost:3000  API http://127.0.0.1:8080
```

Smoke: `npm run qa:api`, manual search on web.

### 4.2 Tier B — Docker Compose

**Prerequisites:** Docker Desktop (or engine) running; `.env` with Vertex variables.

```powershell
# From repo root
.\scripts\deploy\compose-up.ps1
# Or: docker compose up --build
```

With GCP credentials inside containers:

```powershell
$env:GCP_SA_MOUNT="C:\path\to\.secrets\quickpickr-sa.json"
docker compose -f docker-compose.yml -f docker-compose.gcp.yml up --build
```

| Service | Port | Health |
|---------|------|--------|
| web | 3000 | http://localhost:3000 |
| api | 8080 | http://127.0.0.1:8080/health |
| redis | 6379 | internal |

**Indexer (one-off):**

```powershell
docker compose --profile indexer run --rm indexer --help
```

**Artifacts:**

| File | Purpose |
|------|---------|
| [`docker-compose.yml`](../../docker-compose.yml) | api, web, redis |
| [`docker-compose.gcp.yml`](../../docker-compose.gcp.yml) | SA volume overlay |
| [`apps/query-service/Dockerfile`](../../apps/query-service/Dockerfile) | FastAPI image |
| [`apps/web/Dockerfile`](../../apps/web/Dockerfile) | Next.js standalone |
| [`apps/indexer/Dockerfile`](../../apps/indexer/Dockerfile) | Crawl / Vertex push job |

### 4.3 Tier C — Cloud (GCP) — query-service

Example flow (adjust project/region):

1. Build and push image: [`scripts/deploy/cloud-run-query-service.example.sh`](../../scripts/deploy/cloud-run-query-service.example.sh) + [`cloudbuild-query.yaml`](../../cloudbuild-query.yaml).
2. Deploy Cloud Run service `quickpickr-query` (1 vCPU, 1Gi, `min-instances=1` per SAD).
3. Attach runtime SA with Vertex + Secret Manager access.
4. Set `REDIS_URL` to Memorystore when running **>1** instance.
5. Point web `NEXT_PUBLIC_API_URL` to the Cloud Run URL.

**Indexer:** deploy `apps/indexer/Dockerfile` as **Cloud Run Job**; trigger via Cloud Scheduler (hot/warm tiers per SAD §5.3).

**Web:** SAD default **Vercel** for MVP velocity; alternative: build `apps/web/Dockerfile` to Cloud Run + HTTPS load balancer.

### 4.4 Post-deploy verification

| Check | Command / action |
|-------|------------------|
| API health | `GET /health` → `ok` or documented `degraded` |
| Search shape | `POST /v1/search` → 4 retailer rows |
| Web E2E | Search Amul Gold 500 ml @ 560034 |
| CORS | Browser preflight from web origin |
| Rate limit | 31st request → 429 (see integration-plan §7.3) |
| QA automation | `npm run qa:api` against running API |

---

## 5. Rollback procedures

### 5.1 Docker Compose (local)

```powershell
.\scripts\deploy\compose-down.ps1
# Or: docker compose down
# Revert to previous images:
docker compose up -d
# If images were tagged, pin image digest in compose override
```

### 5.2 Cloud Run — query-service

| Step | Action |
|------|--------|
| 1 | `gcloud run services describe quickpickr-query --region=REGION --format='value(status.traffic)'` |
| 2 | Route 100% traffic to **previous revision**: `gcloud run services update-traffic quickpickr-query --to-revisions=REVISION_ID=100 --region=REGION` |
| 3 | Verify `/health` and golden query |
| 4 | If Vertex/config regression: revert Secret Manager version for `VERTEX_SEARCH_SERVING_CONFIG` |

**Do not** roll back only the web client while leaving API contract broken — verify [OpenAPI](../../packages/api-contract/openapi.yaml) compatibility.

### 5.3 Web (Vercel / static)

- Vercel: promote previous deployment from dashboard.
- Container: redeploy prior image digest; rebuild with prior `NEXT_PUBLIC_API_URL` if API URL changed.

### 5.4 Indexer / index data

- Bad index push: pause Scheduler; re-import last known good branch snapshot (operational playbook — out of repo automation).
- Query service rollback does **not** revert Vertex documents.

### 5.5 Emergency disable

- Set Cloud Run `max-instances=0` or remove public invoker (IAM) to stop traffic.
- Display maintenance page on CDN/web if API unavailable.

---

## 6. Status tracking

### 6.1 Configuration artifacts

| Item | Path | Status |
|------|------|--------|
| Query-service Dockerfile | `apps/query-service/Dockerfile` | **Done** |
| Web Dockerfile (standalone) | `apps/web/Dockerfile` | **Done** |
| Indexer Dockerfile | `apps/indexer/Dockerfile` | **Done** |
| docker-compose.yml | repo root | **Done** |
| docker-compose.gcp.yml | SA mount overlay | **Done** |
| .dockerignore | repo root | **Done** |
| .env.docker.example | repo root | **Done** |
| compose-up / compose-down scripts | `scripts/deploy/` | **Done** |
| Cloud Build example | `cloudbuild-query.yaml` | **Done** |
| Cloud Run deploy example | `scripts/deploy/cloud-run-query-service.example.sh` | **Done** |
| `npm run deploy:compose` / `deploy:compose:down` | `package.json` | **Done** |
| Terraform / IaC | — | **Planned** |
| Vercel project config | — | **Planned** |
| GitHub Actions deploy workflow | — | **Planned** |

### 6.2 Environment rollout

| Environment | API | Web | Indexer | Vertex store | Status |
|-------------|-----|-----|---------|--------------|--------|
| dev (native) | uvicorn :8080 | next :3000 | CLI | dev store | **In use** |
| dev (compose) | container :8080 | container :3000 | profile `indexer` | user `.env` | **Ready to test** |
| staging | Cloud Run | TBD | Cloud Run Job | `quickpickr-staging` | **Not deployed** |
| prod | Cloud Run | TBD | Cloud Run Job | `quickpickr-prod` | **Not deployed** |

### 6.3 Release gates (from PRD / QA)

| Gate | Owner | Blocking? | Deploy status |
|------|-------|-----------|---------------|
| `npm run qa:api` pass | @qa.eng | Yes (CI) | Runnable pre-deploy |
| PRD AC-1–AC-4 (Vertex + devices) | @qa.eng | Yes (prod) | Requires staging index |
| SLO 48h staging | Ops | Yes (prod) | Not started |
| Privacy / DPDP notice live | @product-mgr | Yes (prod) | Content not in repo |

---

## 7. Progress log

| When | What |
|------|------|
| 2026-05-21 | deployment-plan.md v1.0: tiers A/B/C, config matrix, rollback, status |
| 2026-05-21 | Dockerfiles (query, web, indexer), docker-compose + gcp overlay, deploy scripts, cloudbuild example |

---

## Sources

- [prd.md](../1.define/prd.md) — release milestones M2, NFRs, API contract
- [sad.md](../2.build/sad.md) §9 Deployment view, §8 Security
- [architecture-plan.md](../2.build/architecture-plan.md) §6 environments
- [integration-plan.md](../2.build/integration-plan.md) §6 configuration matrix, §7 testing
- [backend-plan.md](../2.build/backend-plan.md) §1 Vertex setup

---

## Assumptions

- Primary GCP region: **asia-south1** (India latency); override via `GCP_REGION`.
- Web MVP hosting defaults to **Vercel** per SAD open question OQ-S2 unless team standardizes on Cloud Run.
- Docker Compose is for **local/staging parity**, not production HA.

---

## Open questions

| ID | Question | Default |
|----|----------|---------|
| OQ-D1 | Vercel vs Cloud Run for Next.js in prod? | Vercel for MVP |
| OQ-D2 | Single GCP project vs dev/staging/prod projects? | Separate projects recommended |
| OQ-D3 | Who provisions Memorystore before multi-instance API? | Before prod scale-out |

---

## Audit

| UTC | Persona | Action |
|-----|---------|--------|
| 2026-05-21 | DevOps | deployment-plan.md v1.0 + Docker/compose/deploy scripts |
