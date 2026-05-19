# QuickPickr — Context Summary (Phase 1 Handoff)

| Field | Value |
|-------|-------|
| **Date** | 2026-05-19 |
| **Author** | @product-mgr |
| **Status** | Ready for @system.arch review |

---

## One-paragraph brief

**QuickPickr** helps Indian shoppers who use **Blinkit, Zepto, BigBasket, and Swiggy Instamart** compare prices on a single grocery SKU without opening four apps. The user enters a **product name + pincode**; the system queries a **Vertex AI Search** index of retailer sites, **parses INR prices** from results, and shows a **price-ranked table** with **deep links** to buy on the retailer. Checkout stays on the retailer platform.

---

## Artifacts

| Artifact | Path |
|----------|------|
| MRD | [project-context/1.define/mrd.md](./mrd.md) |
| PRD | [project-context/1.define/prd.md](./prd.md) |
| Legacy copies (root) | `QuickPickr_MRD.md`, `QuickPickr_PRD.md` — superseded by `project-context/1.define/` |

---

## MVP scope (locked for architecture)

**In scope**

- Single-SKU search; pincode; 4 retailers
- Vertex AI Search index + query API + web/mobile clients
- Price rank; freshness labels; outbound CTAs
- Local pincode cache; no accounts
- **13 structured user stories** (MRD §4 / PRD §5) with acceptance criteria
- **User Trust Risk register** (UTR-01–10) — release blockers on price accuracy, SKU match, deep links

**Out of scope v1**

- Cart, checkout, payments
- Basket compare; loyalty; extra retailers

---

## Key NFRs for @system.arch

| Area | Target |
|------|--------|
| Latency P50 / P95 | 1.5s / 3s |
| Freshness | ≤5 min (95% rows) |
| Uptime | 99.5% |
| Privacy | No login; local pincode; DPDP notice |

---

## Open questions requiring architect input

1. Vertex AI Search index schema and per-retailer isolation strategy
2. Crawler deployment model (Cloud Run jobs vs managed pipeline)
3. Match-confidence algorithm: rules-only vs LLM grounding in query path
4. Cache layer: edge vs Redis vs in-process for MVP scale

---

## Recommended next steps

1. **@system.arch** — Run `*create-sad` or `*create-sad --mvp` → `project-context/1.define/sad.md`
2. Set `AAMAD_TARGET_RUNTIME` (`cursor-sdk` recommended for TS/Node MVP per adapter rules)
3. **@project.mgr** — `*setup-project` after SAD approval

---

## Handoff checklist

- [x] MRD: market, personas, structured user stories, user trust risk, competition, KPIs, risks
- [x] PRD: structured user stories, user trust risk, FR/NFR, API sketch, acceptance criteria, release plan
- [x] Sources, Assumptions, Open Questions, Audit on both artifacts
- [ ] Stakeholder sign-off on MRD/PRD
- [ ] SAD created
- [ ] Runtime selected and recorded in SAD Audit

---

## Audit

| Timestamp (UTC) | Persona | Action |
|-----------------|---------|--------|
| 2026-05-19T00:00:00Z | @product-mgr | Context summary for Define → Build handoff |
| 2026-05-19T12:00:00Z | @product-mgr | Updated for structured user stories and user trust risk sections |
