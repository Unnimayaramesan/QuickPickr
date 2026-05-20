# QuickPickr — QA Plan

| Field | Value |
|-------|-------|
| **Version** | 1.1 |
| **Updated** | 2026-05-21 |
| **Author** | @qa.eng |
| **Inputs** | [prd.md](../1.define/prd.md), [sad.md](./sad.md), [frontend-plan.md](./frontend-plan.md), [backend-plan.md](./backend-plan.md), [integration-plan.md](./integration-plan.md), [AGENTS.md](../../AGENTS.md), [.cursor/agents/dev-crew.md](../../.cursor/agents/dev-crew.md) |

---

## 1. Scope

This plan covers **functional and smoke validation** of the QuickPickr MVP (web, mobile, FastAPI query service, shared packages) against the PRD and integration release matrix (**[integration-plan §7](./integration-plan.md#7-qa--testing-strategy)**).

**Out of scope for this run (documented as N/T — not tested / deferred):**

- Staged Vertex index coverage required for **PRD AC-1** (≥3 `available` retailers) and golden-set regression at scale.
- Playwright / Maestro device matrix for **AC-4** deep links.
- k6 / Cloud Monitoring for **AC-3** latency percentiles.
- Formal trust-blocker execution **AC-T1 / AC-T3 / AC-T5** (PRD §6.3, §13.2) without product sign-off procedure.

---

## 2. Test environment (this execution)

| Item | Value |
|------|-------|
| Host OS | Windows 10 |
| Node | Per repo (npm workspaces) |
| Python | 3.14 (user global env with FastAPI deps) |
| Branch | `feature/qa` (local) |
| Vertex / `.env` | Serving config **not** set in smoke path; health reports `status: error`; Discovery calls fail with `RESOURCE_PROJECT_INVALID` — rows still returned as `error` per retailer (graceful degradation). |
| Re-run session | 2026-05-21 — full automated suite re-executed from repo root |

---

## 3. Automated runs — summary

| Command | Expected | Actual | Status |
|---------|----------|--------|--------|
| `npm run verify:contract` | OpenAPI snapshot present, non-empty | OK (6110 bytes) | **Pass** |
| `npm run typecheck` | api-client, shared, web compile | All `tsc --noEmit` clean | **Pass** |
| `npm run typecheck -w @quickpickr/mobile` | Mobile TS clean | Clean | **Pass** |
| `npm run build:web` | Next.js production build | Next.js **14.2.35**; compiled; **7** static routes | **Pass** |
| `npm run qa:api` (or `python scripts/qa_api_smoke.py`) | 200 `/health`; 200 `/v1/search` with 4 retailers; 400/422 bad pincode | As expected; stderr noisy when Vertex misconfigured (see **ISS-QA-004**) | **Pass** |
| `QA_RATE_LIMIT=1` + `npm run qa:api` | 31st POST → **429** | **429** on request 31 | **Pass** |

---

## 4. Test scenarios and cases

### 4.1 API — `apps/query-service`

| ID | Scenario | Steps | Expected | Actual | Status |
|----|----------|-------|----------|--------|--------|
| API-01 | Health | `GET /health` | 200; JSON includes `status`, `vertexConfigured`, `credentialsPathSet`, `message` | `status: error` when serving config empty; keys present | **Pass** |
| API-02 | Search — happy path shape | `POST /v1/search` valid body + `X-Session-Id` | 200; `query`/`pincode` echoed; **4** rows (blinkit, zepto, bigbasket, instamart); `meta.latencyMs` | 4 rows; all retailers present | **Pass** |
| API-03 | Search — validation | Pincode `56003` (5 digits) | **400** or **422** (FastAPI / Pydantic) | **422** | **Pass** |
| API-04 | Rate limit | Same session, 31 requests/min | 31st → **429** | **429** with detail message | **Pass** |
| API-05 | Degraded Vertex | Invalid/missing serving resource | No 5xx on `/v1/search`; per-row `error` or `unavailable` | `error` rows + stack traces in logs (**ISS-QA-004**) | **Pass** (behavior); **Fail** (log hygiene) |

### 4.2 Frontend — web (`apps/web`)

| ID | Scenario | Steps | Expected | Actual | Status |
|----|----------|-------|----------|--------|--------|
| WEB-01 | Build | `npm run build:web` | Success, typecheck in build | Success | **Pass** |
| WEB-02 | Typecheck | Root `typecheck` includes web | Clean | Clean | **Pass** |
| WEB-03 | Results + telemetry props | Code review: `HomeSearch` → `ResultsTable` passes `searchedAt` for stale analytics | Prop wired | Confirmed in `HomeSearch.tsx` / `ResultsTable.tsx` | **Pass** (static) |
| WEB-04 | Geocode fetch | `geocode.ts` uses bound `fetch` | Avoid Illegal invocation | `fetch.bind(globalThis)` | **Pass** (static) |
| WEB-05 | E2E golden path (browser) | `npm run dev`, search Amul Gold 560034 | Table, Buy links, skeleton ≥200ms | Not executed this session | **N/T** |

### 4.3 Mobile (`apps/mobile`)

| ID | Scenario | Steps | Expected | Actual | Status |
|----|----------|-------|----------|--------|--------|
| MOB-01 | Typecheck | `npm run typecheck -w @quickpickr/mobile` | Clean | Clean | **Pass** |
| MOB-02 | Stale telemetry | Code review after search | `stale_row_shown` when `crawledAt` stale | Loop in `HomeScreen.tsx` | **Pass** (static) |
| MOB-03 | E2E device / AC-4 | Expo on device | PDP opens per retailer | Not executed | **N/T** |

### 4.4 End-to-end (product)

| ID | Scenario | PRD ref | Expected | Actual | Status |
|----|----------|---------|----------|--------|--------|
| E2E-01 | Amul Gold @ 560034 | §13 AC-1 | ≥3 `available` | Blocked without staging Vertex + index | **Blocked** |
| E2E-02 | Price accuracy | AC-2 | ±2% vs live | Manual / not run | **N/T** |
| E2E-03 | Latency | AC-3 | P95 &lt; 3s @ 1k queries | Not measured | **N/T** |
| E2E-04 | `milk` low confidence | AC-5 | `matchConfidence: low` + label | Needs index + UI assert | **N/T** |
| E2E-05 | Nonsense query | AC-6 | 200 + graceful empty | Partially covered by API shape; Macallan not explicitly run | **N/T** |
| E2E-06 | Pincode persistence | AC-7 | 110001 survives restart | Manual app test | **N/T** |
| E2E-07 | Web vs mobile rank | AC-8 | Same order within TTL | Not compared | **N/T** |

---

## 5. AAMAD “Application Crew” / agent definitions

**Note:** Cursor/AAMAD **personas are IDE-time orchestration roles**, not runtime services. Validation here = **definitions present + epic artifacts + repo alignment**, not invoking agents inside the app.

| Persona | Definition source | Expected artifact / evidence | Verified | Status |
|---------|-------------------|------------------------------|----------|--------|
| @product-mgr | `product-mgr.md` | PRD / MRD in `project-context/1.define/` | `prd.md` reviewed (§13 AC) | **Pass** |
| @system-arch | `system-arch.md` | SAD | `sad.md` present | **Pass** |
| @project-mgr | `project-mgr.md` | `setup.md`, env scaffolding | `project-context/2.build/setup.md` referenced | **Pass** |
| @frontend-eng | `frontend-eng.md` | Web UI, `frontend.md` / plan | `apps/web`, `frontend-plan.md` | **Pass** |
| @backend-eng | `backend-eng.md` | Query service, `backend.md` / plan | `apps/query-service`, `backend-plan.md`, `backend.md` | **Pass** |
| @integration-eng | `integration-eng.md` | Wiring, `integration.md` + plan | `integration-plan.md`, OpenAPI, clients | **Pass** |
| @qa-eng | `qa-eng.md` | `qa.md`, coverage log | `qa.md`, this `qa-plan.md` | **Pass** |
| Dev crew rollup | `dev-crew.md` | All roles described | File present | **Pass** |

---

## 6. Issues found

| ID | Severity | Area | Description | Resolution / owner |
|----|----------|------|-------------|-------------------|
| ISS-QA-001 | **High** | Repo hygiene | `.gitignore` contained bare `.` and `*.json`, which could hide **all** JSON from git status, breaking `package.json`, `config/*.json`, etc. | **Fixed (re-run 2026-05-21):** removed `.` and `*.json`; keep `.secrets/` + standard ignores. Re-verify with `git status` after pull/merge — pattern has regressed before on some branches. |
| ISS-QA-002 | Medium | Test harness | `TestClient` without app **lifespan** left `app.state.rate_limiter` unset → 500 on `/v1/search`. | **Fixed:** `scripts/qa_api_smoke.py` uses `with TestClient(app) as client:`. |
| ISS-QA-003 | Low | DX | Root `npm run typecheck` omits `@quickpickr/mobile`; contributors may forget mobile. | Documented in [integration-plan §7.1](./integration-plan.md#71-what-runs-in-repo-today); consider extending root script later. |
| ISS-QA-004 | Low | Observability | When Vertex returns API errors (e.g. invalid resource), `search_service` logs **full tracebacks** per retailer → very noisy stderr in dev/CI. | Suggest: log summary + `exc_info` only for unexpected exceptions; track as backend hardening. |

---

## 7. Status tracking (summary)

| Area | Pass | Fail | Blocked | N/T |
|------|------|------|---------|-----|
| Contract / TS build | 4 | 0 | 0 | 0 |
| API smoke | 4 | 0 | 0 | 0 |
| Web static / build | 3 | 0 | 0 | 1 |
| Mobile static | 2 | 0 | 0 | 1 |
| PRD E2E / AC | 0 | 0 | 1 | 6 |
| Agent definitions | 8 | 0 | 0 | 0 |

**Release recommendation:** **Not ready** for production against PRD **AC-1–AC-3** without configured Vertex + staging validation. **Local MVP wiring** (types, build, API contract shape, rate limit, graceful error rows) **acceptable** for dev iteration.

---

## 8. How to re-run

```powershell
cd c:\Users\welcome\Documents\quick-pickr-project
npm run verify:contract
npm run typecheck
npm run typecheck -w @quickpickr/mobile
npm run build:web
npm run qa:api
$env:QA_RATE_LIMIT="1"; npm run qa:api
```

Full stack manual E2E: `npm run dev` → http://localhost:3000 (see [README](../../README.md)).

---

## Sources

- [prd.md](../1.define/prd.md) §13 (acceptance), §7.2 (edge journeys), §6.3 (trust)
- [sad.md](./sad.md) — testing / NFR expectations
- [integration-plan.md](./integration-plan.md) §7 — QA strategy and smoke checklist
- [frontend-plan.md](./frontend-plan.md), [backend-plan.md](./backend-plan.md)

---

## Assumptions

- Python on PATH can import `app.main` when `apps/query-service` is on `PYTHONPATH` (smoke script sets this).
- No PRD content was invented; blocked/N/T items reference explicit PRD gaps or environment needs.

---

## Open questions

- Should root `typecheck` include `mobile` by default (adds CI time)?
- Target CI runner: is Python 3.14 acceptable vs pinning 3.11 per backend-plan?

---

## Audit

| UTC | Persona | Action |
|-----|---------|--------|
| 2026-05-20 | @qa.eng | qa-plan.md v1.0: matrix, automated runs, issues, crew mapping, ISS-QA-001 fix |
| 2026-05-21 | @qa.eng | qa-plan.md v1.1: re-ran verify:contract, typecheck (+ mobile), build:web, qa:api (+ rate limit); `.gitignore` repaired again; backend.md reflected in crew table |
