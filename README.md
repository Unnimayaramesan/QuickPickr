# QuickPickr

**One search. Four apps. Best price.**

QuickPickr is a quick-commerce price comparison product for shoppers in India. Enter a product name and pincode once, compare live prices across **Blinkit**, **Zepto**, **BigBasket**, and **Swiggy Instamart**, and jump to the cheapest retailer to complete your purchase there.

This repository is built with the [AAMAD](https://pypi.org/project/aamad/) (AI-Assisted Multi-Agent Application Development) framework. **Phase 1** (MRD, PRD, SAD) is complete. **Phase 2** delivers an MVP monorepo: Next.js web, Expo mobile, FastAPI query service, shared TypeScript packages, and Vertex AI Search integration—see [Getting Started](#getting-started) and [npm scripts](#npm-scripts-root).

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Value Proposition](#value-proposition)
- [Key Features](#key-features)
- [Application Architecture](#application-architecture)
- [Development Workflow (AAMAD Agents)](#development-workflow-aamad-agents)
- [Getting Started](#getting-started)
- [npm scripts (root)](#npm-scripts-root)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Next Steps for Contributors](#next-steps-for-contributors)
- [License](#license)

---

## Project Overview

Indian quick-commerce shoppers routinely use multiple apps for groceries and household essentials. The same SKU can differ by **10–40%** between platforms on any given day, but finding the best price means opening **four separate apps**, searching each one, and comparing manually—a **2–5 minute** ritual per item.

QuickPickr replaces that workflow with a single search:

1. Enter a product (e.g. `Amul Gold 500 ml`) and your **6-digit pincode**.
2. View a **price-ranked table** for all four retailers.
3. Tap **Buy on [Retailer]** to open that retailer’s product page and checkout on their platform.

**Technical approach (MVP):** A [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) index over retailer catalog pages, a stateless query API that parses INR prices from search results, and web (Next.js) plus mobile (React Native) clients.

| Attribute | Detail |
|-----------|--------|
| **Target users** | Urban India shoppers using 2+ quick-commerce apps |
| **Retailers (v1)** | Blinkit, Zepto, BigBasket, Swiggy Instamart |
| **Monetization (future)** | Affiliate links, clearly labeled sponsored rows |
| **Status** | Define complete; **Build MVP** — web, mobile, query API in repo ([architecture-plan](project-context/2.build/architecture-plan.md)) |
| **Primary persona** | Priya — Bengaluru professional, price-sensitive on staples |

---

## Problem Statement

**Today:** To find the cheapest price for one item, a shopper opens Blinkit, Zepto, BigBasket, and Instamart, repeats the same search in each app, scrolls past sponsored results, normalizes pack sizes mentally, and switches between apps to compare. Most people stop after one or two apps and pay an unobserved premium.

**Job to be done:** *When I need to buy a known grocery item, help me find the cheapest price across the apps I already use, in under a minute, without making me leave the retailer’s checkout I trust.*

---

## Value Proposition

| For shoppers | For the ecosystem |
|--------------|-------------------|
| **~30 seconds** instead of a multi-app hunt | Discovery layer—no inventory, cart, or payments |
| **One ranked table**—cheapest option is obvious | Checkout and trust stay with retailers |
| **Honest comparison**—freshness timestamps, “closest match” labels | Repeatable daily use on high-frequency staples |
| **No account required** in v1 | Built for trust (see [User Trust Risk](project-context/1.define/prd.md#6-user-trust-risk) in PRD) |

QuickPickr does **not** process payments or hold inventory. It is a **discovery and comparison** product that sends shoppers to the retailer they choose.

---

## Key Features

### MVP (v1 — in scope)

| Feature | Description |
|---------|-------------|
| **Unified search** | Product name + pincode → prices from four retailers in one table |
| **Price-ranked results** | Sorted ascending by INR price; “Lowest price” label on cheapest row |
| **Retailer deep links** | One-tap **Buy on [Retailer]** opens the product detail page |
| **Complete coverage UI** | All four retailer slots shown (available, unavailable, or error) |
| **Like-for-like display** | Product title, pack size, unit price (₹/ml or ₹/g where possible) |
| **Price freshness** | “Updated N min ago”; stale rows labeled when index age >5 min |
| **Match confidence** | “Closest match” badge when SKU equivalence is uncertain |
| **Local pincode memory** | Pincode cached on device—no login required |
| **Trust transparency** | Footer copy: prices sourced from retailer websites |
| **Progressive loading** | Skeleton UI within 200ms; partial results if one retailer is slow |

### Planned (v1.1+)

| Feature | Priority |
|---------|----------|
| GPS → pincode (“Use my location”) | P1 |
| Search history (last 20 queries) | P1 |
| Hindi UI | P1 |
| Native app deep links (iOS/Android) | P1 |

### Explicitly out of scope (v1)

- In-app checkout, cart, or payments  
- Multi-retailer basket optimization  
- User accounts / login  
- Retailers beyond the four named platforms  

Full requirements: [project-context/1.define/prd.md](project-context/1.define/prd.md)

---

## Application Architecture

QuickPickr has three logical layers. Full specification: [project-context/2.build/sad.md](project-context/2.build/sad.md).

```mermaid
flowchart TB
  subgraph Clients
    Web[Web App - Next.js]
    Mobile[Mobile App - React Native]
  end

  subgraph API["Query Layer"]
    QS[Query Service - Cloud Run]
    Cache[(Cache - 60s TTL)]
  end

  subgraph Data["Data Layer"]
    VAS[Vertex AI Search Index]
    Crawler[Indexer / Crawler]
  end

  Web --> QS
  Mobile --> QS
  QS --> Cache
  QS --> VAS
  Crawler --> VAS
```

### Layer responsibilities

| Layer | Components | Role |
|-------|------------|------|
| **Client** | Next.js (web), React Native (iOS/Android) | Input validation, pincode cache, results UI, deep links, analytics |
| **Query API** | FastAPI on Cloud Run | `POST /v1/search` — parallel Vertex AI Search per retailer, INR parsing, rank by price |
| **Indexing** | Crawler + Vertex AI Search | Index retailer catalog pages; refresh hot SKUs every 2–5 minutes |

### Search flow

1. Client sends `{ query, pincode }` to the query API.  
2. API checks a 60-second cache, then issues **four parallel** Vertex AI Search queries (one per retailer), scoped by serviceability zone.  
3. API parses prices from structured fields and snippets (regex fallback for `₹` amounts).  
4. API returns JSON sorted by `finalPriceInr` ascending.  
5. Client renders the table; user taps through to the retailer PDP.

### API contract (MVP)

```http
POST /v1/search
Content-Type: application/json

{
  "query": "Amul Gold 500 ml",
  "pincode": "560034"
}
```

OpenAPI snapshot: `packages/api-contract/openapi.yaml` (regenerate with `python scripts/export_openapi.py` when the FastAPI schema changes). See [PRD §12](project-context/1.define/prd.md#12-api-contract-mvp) for the full response schema.

### Performance targets

| Metric | Target |
|--------|--------|
| P50 latency (submit → first result) | <1.5s |
| P95 latency | <3.0s |
| Price freshness | ≤5 min for 95% of rows |
| API uptime | 99.5% monthly |

---

## Development Workflow (AAMAD Agents)

QuickPickr is developed using **AAMAD persona agents** in Cursor (or compatible IDEs). Each agent owns a phase or epic and writes auditable artifacts under `project-context/`.

```mermaid
flowchart LR
  subgraph Define["Phase 1 — Define"]
    PM["@product-mgr"]
    ARCH["@system.arch"]
    PM --> MRD[MRD + PRD]
    MRD --> ARCH
    ARCH --> SAD[SAD]
  end

  subgraph Build["Phase 2 — Build"]
    PROJ["@project.mgr"]
    FE["@frontend.eng"]
    BE["@backend.eng"]
    INT["@integration.eng"]
    QA["@qa.eng"]
    SAD --> PROJ
    PROJ --> FE
    PROJ --> BE
    FE --> INT
    BE --> INT
    INT --> QA
  end

  subgraph Deliver["Phase 3 — Deliver"]
    DEVOPS[DevOps]
    QA --> DEVOPS
  end
```

### Agent personas and roles

| Agent | Phase | Role | Primary output |
|-------|-------|------|----------------|
| **@product-mgr** | Define | Market research, MRD, PRD, context handoff | `project-context/1.define/mrd.md`, `prd.md` |
| **@system.arch** | Define | Solution architecture, NFRs, technical decisions | `project-context/2.build/sad.md` |
| **@project.mgr** | Build | Scaffold repo, dependencies, environment | `project-context/2.build/setup.md` |
| **@frontend.eng** | Build | Web/mobile UI, search and results screens | `frontend.md`, [frontend-plan.md](project-context/2.build/frontend-plan.md) |
| **@backend.eng** | Build | Query API, Vertex AI Search integration, indexer | `backend.md`, [backend-plan.md](project-context/2.build/backend-plan.md) |
| **@integration.eng** | Build | Wire clients to API, end-to-end flows | `integration.md`, [integration-plan.md](project-context/2.build/integration-plan.md) |
| **@qa.eng** | Build | Smoke tests, golden-set validation, trust ACs | `qa.md`, [qa-plan.md](project-context/2.build/qa-plan.md) |

Invoke agents in Cursor chat with `@product-mgr`, `@backend.eng`, etc. See [AGENTS.md](AGENTS.md) and [.cursor/agents/](.cursor/agents/) for full persona definitions.

### Phase 2 epics

| Epic | Persona | Command | Epic log | Detailed plan |
|------|---------|---------|----------|---------------|
| Setup | @project.mgr | `*setup-project` | `setup.md` | — |
| Frontend | @frontend.eng | `*develop-fe` | `frontend.md` | `frontend-plan.md` |
| Backend | @backend.eng | `*develop-be` | `backend.md` | `backend-plan.md` |
| Integration | @integration.eng | `*integrate-api` | `integration.md` | `integration-plan.md` |
| QA | @qa.eng | `*qa` | `qa.md` | `qa-plan.md` |

All paths under `project-context/2.build/` unless noted.

### Runtime adapter

Set the backend runtime for the generated MVP:

```bash
# One of: crewai (default) | claude-agent-sdk | cursor-sdk
export AAMAD_TARGET_RUNTIME=cursor-sdk
```

Adapter rules live in `.cursor/rules/adapter-*.mdc`. The **search/index path** uses Vertex AI Search on GCP regardless of adapter choice.

---

## Getting Started

### Prerequisites

| Tool | Purpose |
|------|---------|
| [Cursor](https://cursor.com/) (recommended) or VS Code + Copilot | AAMAD agent workflows |
| [Node.js](https://nodejs.org/) 18+ | npm workspaces (web, mobile, shared packages) |
| [Python](https://www.python.org/) 3.11+ | FastAPI query service (`apps/query-service`) |
| [Google Cloud](https://cloud.google.com/) account | Vertex AI Search (Discovery Engine API) |
| Git | Version control |

Optional: `pip install aamad` if re-initializing framework files in a new clone.

### 1. Clone the repository

```bash
git clone <repository-url>
cd quick-pickr-project
```

### 2. Read the requirements

```bash
# Market and product context
project-context/1.define/mrd.md    # Market requirements, personas, trust risks
project-context/1.define/prd.md    # Functional specs, API, acceptance criteria
project-context/1.define/context-summary.md
```

### 3. Use AAMAD in Cursor

1. Open the project in Cursor.  
2. Start a new agent chat and invoke the relevant persona (e.g. `@system.arch`).  
3. Follow [CHECKLIST.md](CHECKLIST.md) for phase order.  
4. Reference files with `@project-context/1.define/prd.md` in prompts.

### 4. Environment variables

1. Copy the template and fill in Vertex + GCP credentials (see [backend-plan §1 — Vertex setup](./project-context/2.build/backend-plan.md#1-vertex-ai-search-discovery-engine--role-in-quickpickr)):

```powershell
copy .env.example .env
# Edit .env: VERTEX_SEARCH_SERVING_CONFIG, GOOGLE_APPLICATION_CREDENTIALS
```

2. Web client → API URL:

```powershell
copy apps\web\.env.local.example apps\web\.env.local
# Ensure NEXT_PUBLIC_API_URL=http://127.0.0.1:8080 for local FastAPI
```

Never commit `.env`, `.secrets/`, or service-account JSON. Do **not** add a blanket `*.json` rule to `.gitignore`—it hides tracked config and manifests (see [qa-plan ISS-QA-001](project-context/2.build/qa-plan.md#6-issues-found)).

### 5. Install dependencies (fresh clone)

From the repository root:

```powershell
npm install --include=optional
pip install -r apps\query-service\requirements.txt
```

Use a Python 3.11+ virtual environment if you prefer (`python -m venv .venv` then activate before `pip install`).

### 6. Happy path — web + API together

Start **Next.js (port 3000)** and the **FastAPI query service (port 8080)** with one command:

```powershell
npm run dev
```

Then open **http://localhost:3000**, enter **Amul Gold 500 ml** and pincode **560034**, and search. You should see a **four-row** ranked table (available / unavailable / error per retailer), **deep-link Buy** buttons using HTTPS PDP URLs (native schemes from `config/retailers.json` apply where applicable), and latency/cache hints under the table.

**Smoke-check API only (PowerShell):** with the API running (`npm run dev` or `npm run dev:api`):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8080/v1/search -Method POST -ContentType "application/json" -Body '{"query":"Amul Gold 500 ml","pincode":"560034"}'
```

For automated checks without a browser, see [§9 Verify and test](#9-verify-and-test-no-browser).

### 7. Mobile (optional)

```powershell
npm run dev:mobile
```

Set `EXPO_PUBLIC_API_URL` (e.g. in `.env` at repo root or Expo env) to your machine’s reachable API URL when testing on a device.

### 8. Vertex-only CLI verify

```powershell
python scripts\verify_vertex.py "Amul Gold 500 ml"
```

See [setup.md](./project-context/2.build/setup.md) for troubleshooting (`403`, empty results, etc.).

### 9. Verify and test (no browser)

From the repo root:

```powershell
npm run verify:contract    # OpenAPI snapshot present
npm run typecheck          # api-client, shared, web
npm run typecheck -w @quickpickr/mobile
npm run build:web          # Next.js production build
npm run qa:api             # In-process /health + /v1/search smoke
```

Optional rate-limit check: `$env:QA_RATE_LIMIT="1"; npm run qa:api` (expects **429** on the 31st request for the same `X-Session-Id`).

Latest automated results: **[qa-plan.md](./project-context/2.build/qa-plan.md)** §3. Wiring and release checklist: **[integration-plan.md](./project-context/2.build/integration-plan.md)** §7.

### 10. Deployment (Docker / cloud)

Full plan: **[deployment-plan.md](./project-context/3.deliver/deployment-plan.md)**.

**Docker Compose** (API + web + Redis):

```powershell
docker compose up --build
# With GCP SA mounted for Vertex inside containers:
$env:GCP_SA_MOUNT="C:\path\to\.secrets\your-sa.json"
docker compose -f docker-compose.yml -f docker-compose.gcp.yml up --build
```

Helpers: `scripts/deploy/compose-up.ps1`, `compose-down.ps1`. See [`.env.docker.example`](./.env.docker.example).

**Production target (GCP):** Cloud Run for `apps/query-service`, Cloud Run Jobs for `apps/indexer`, Vertex AI Search, optional Memorystore — example in `scripts/deploy/cloud-run-query-service.example.sh`.

---

## npm scripts (root)

| Script | What it does |
|--------|----------------|
| `npm run dev` | **Web (:3000)** + **API (:8080)** via [concurrently](https://www.npmjs.com/package/concurrently) |
| `npm run dev:web` | Next.js only |
| `npm run dev:api` | FastAPI only (`scripts/run-query-service-dev.cjs`, sets `PYTHONPATH`) |
| `npm run dev:mobile` | Expo dev server |
| `npm run build:web` | Production Next.js build |
| `npm run typecheck` | TypeScript: api-client, shared, web |
| `npm run verify:contract` | Ensures `packages/api-contract/openapi.yaml` exists |
| `npm run qa:api` | Python smoke: health, search shape, validation (see `scripts/qa_api_smoke.py`) |

---

## Deployment

| Tier | When to use | Entry |
|------|-------------|--------|
| **Local** | Daily development | `npm run dev` |
| **Docker Compose** | Stack parity, demos, pre-release smoke | `docker compose up --build` |
| **GCP** | Staging / production | [deployment-plan.md](./project-context/3.deliver/deployment-plan.md) §4.3 |

Images: `apps/query-service/Dockerfile`, `apps/web/Dockerfile` (Next.js `standalone`), `apps/indexer/Dockerfile` (batch job).

---

## Project Structure

```
quick-pickr-project/
├── README.md                 # This file
├── AGENTS.md                 # AAMAD agent index
├── CHECKLIST.md              # Define → Build → Deliver checklist
├── package.json              # Root workspaces + dev/qa scripts
├── .env.example              # Vertex + API URLs (copy to .env)
│
├── apps/
│   ├── web/                  # Next.js 14 — search UI, history, settings
│   ├── mobile/               # Expo — React Native client
│   └── query-service/        # FastAPI — POST /v1/search, GET /health
│
├── packages/
│   ├── api-contract/         # OpenAPI snapshot (openapi.yaml)
│   ├── api-client/           # QuickPickrClient (web + mobile)
│   ├── shared/               # sort, freshness, analytics, affiliates
│   └── design-tokens/
│
├── config/
│   ├── retailers.json        # Deep-link patterns per retailer
│   └── affiliates.json       # Optional CTA query params
│
├── scripts/
│   ├── deploy/               # compose-up/down, Cloud Run example
│   ├── run-query-service-dev.cjs
│   ├── qa_api_smoke.py
│   └── verify_vertex.py
│
├── project-context/
│   ├── 1.define/             # MRD, PRD, context-summary
│   ├── 2.build/              # SAD, plans, epic logs (setup, frontend, backend, …)
│   └── 3.deliver/            # Phase 3 — deployment-plan, deliver
│
├── docker-compose.yml        # api + web + redis
├── docker-compose.gcp.yml    # optional SA mount overlay
├── .cursor/                  # AAMAD agents, rules, templates
├── QuickPickr_MRD.md         # → project-context/1.define/mrd.md
└── QuickPickr_PRD.md         # → project-context/1.define/prd.md
```

**Local URLs:** Web **http://localhost:3000** · API **http://127.0.0.1:8080** · Dev UI (optional) **http://127.0.0.1:8080/** when static assets are present.

---

## Documentation

| Document | Description |
|----------|-------------|
| [MRD](project-context/1.define/mrd.md) | Market opportunity, personas, structured user stories, user trust risk |
| [PRD](project-context/1.define/prd.md) | Features, NFRs, API contract, acceptance criteria, release plan |
| [Context summary](project-context/1.define/context-summary.md) | Phase 1 handoff for architects and builders |
| [SAD](project-context/2.build/sad.md) | Solution architecture (FastAPI, Vertex AI Search, clients) |
| [Architecture plan](project-context/2.build/architecture-plan.md) | Milestones, SLOs, implementation status |
| [Setup](project-context/2.build/setup.md) | Environment and local runbook |
| [Backend plan](project-context/2.build/backend-plan.md) | Vertex env, query service design |
| [Backend log](project-context/2.build/backend.md) | @backend.eng epic summary |
| [Frontend plan](project-context/2.build/frontend-plan.md) | Web/mobile scope |
| [Frontend log](project-context/2.build/frontend.md) | @frontend.eng epic summary |
| [Integration plan](project-context/2.build/integration-plan.md) | E2E wiring, env matrix, **§7 testing** |
| [QA plan](project-context/2.build/qa-plan.md) | Test matrix, last run results, defects |
| [Deployment plan](project-context/3.deliver/deployment-plan.md) | Docker, Compose, GCP Cloud Run, rollback |
| [CHECKLIST.md](CHECKLIST.md) | Step-by-step AAMAD execution |
| [AGENTS.md](AGENTS.md) | Agent persona quick reference |

---

## Next Steps for Contributors

### If you are new to the project

1. Read the [PRD](project-context/1.define/prd.md) executive summary and [User Trust Risk](project-context/1.define/prd.md#6-user-trust-risk) section—accuracy and deep links are release blockers.  
2. Review [structured user stories](project-context/1.define/prd.md#5-user-stories-structured-format) (US-001–US-013).  
3. Check [CHECKLIST.md](CHECKLIST.md) for current phase status.

### Recommended build sequence

| Step | Owner | Action | Output |
|------|-------|--------|--------|
| 1 | @system.arch | SAD + architecture plan | [sad.md](project-context/2.build/sad.md), [architecture-plan.md](project-context/2.build/architecture-plan.md) |
| 2 | @project.mgr | `*setup-project` | [setup.md](project-context/2.build/setup.md), `.env.example` |
| 3 | @backend.eng | `*develop-be` | `apps/query-service`, [backend.md](project-context/2.build/backend.md) |
| 4 | @frontend.eng | `*develop-fe` | `apps/web`, `apps/mobile`, [frontend.md](project-context/2.build/frontend.md) |
| 5 | @integration.eng | `*integrate-api` | `npm run dev`, [integration-plan.md](project-context/2.build/integration-plan.md) |
| 6 | @qa.eng | `*qa` | `npm run qa:api`, [qa-plan.md](project-context/2.build/qa-plan.md); staging Vertex for PRD AC-1–AC-4 |

**Current gap for production sign-off:** PRD golden-path tests (≥3 priced retailers, live price spot-check, device deep links) need a **configured Vertex index** and staging environment—not only in-repo smoke tests.

### How to contribute

- **Requirements:** Open issues or PRs against `project-context/1.define/` with clear traceability to story IDs (e.g. US-007, UTR-01).  
- **Code (Phase 2+):** Follow the epic owned by your persona; document decisions in the matching `project-context/2.build/*.md` artifact.  
- **Trust and quality:** Do not merge changes that weaken freshness labels, SKU match conservatism, or four-retailer completeness without PM sign-off.  
- **Modules:** Use a **fresh Cursor chat per epic** (see `.cursor/rules/development-workflow.mdc`) to keep context bounded.

### Open questions (need resolution before or during build)

| Topic | Default if unresolved |
|-------|---------------------|
| Stale price UX (>5 min) | Show row with “Price may be outdated” |
| Delivery time in ranking | Price only in v1 |
| Multi-item basket | Deferred to v2 |

See [PRD Open Questions](project-context/1.define/prd.md#open-questions).

---

## License

Licensed under the Apache License 2.0 (per AAMAD framework defaults).

---

> **QuickPickr** — Compare quick-commerce prices in India without opening four apps.  
> Built with **AAMAD** for auditable, multi-agent development.
