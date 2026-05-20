# QuickPickr — Frontend Epic Log

| Field | Value |
|-------|-------|
| **Author** | @frontend.eng |
| **Plan** | [frontend-plan.md](./frontend-plan.md) |
| **Status** | MVP implemented — pending device QA |

---

## Summary

Delivered **Next.js 14 web** (`apps/web`) and **Expo React Native mobile** (`apps/mobile`) sharing:

- `packages/api-contract/openapi.yaml`
- `packages/api-client` (`QuickPickrClient`)
- `packages/design-tokens`
- `packages/shared` (sort, i18n, freshness, analytics, affiliate)

---

## Run locally

```powershell
# Terminal 1 — API
cd apps\query-service
$env:PYTHONPATH="."
uvicorn app.main:app --reload --port 8080

# Terminal 2 — Web
cd c:\Users\welcome\Documents\quick-pickr-project
npm install
copy apps\web\.env.local.example apps\web\.env.local
npm run dev:web
# http://localhost:3000

# Terminal 3 — Mobile (optional)
npm run dev:mobile
# Set EXPO_PUBLIC_API_URL; use LAN IP for physical device
```

---

## Decisions

| Topic | Decision |
|-------|----------|
| Monorepo | npm workspaces |
| API client | Hand-written TS aligned to OpenAPI |
| Mobile | Expo 51 + React Navigation |
| Geocode (web) | Nominatim reverse geocode |
| Geocode (mobile) | expo-location reverseGeocode |
| Stale rows | Show warning when age > 5 min |
| Affiliate | `config/affiliates.json` (all disabled default) |

---

## Acceptance status

| ID | Criterion | Status |
|----|-----------|--------|
| AC-FE-4 | Pincode persists | Pass (localStorage / AsyncStorage) |
| AC-FE-5 | Identical sort web/mobile | Pass (`sortResults` shared) |
| AC-FE-1 | Amul Gold / 560034 E2E | Pending — needs priced index rows |
| AC-FE-2 | P95 < 3s | Pending load test |
| AC-FE-3 | Mobile PDP deep link | Pending device test with valid buyUrl |

---

## Audit

| Timestamp (UTC) | Persona | Action |
|-----------------|---------|--------|
| 2026-05-19T23:00:00Z | @frontend.eng | Web + mobile MVP; shared packages; frontend-plan updated |
