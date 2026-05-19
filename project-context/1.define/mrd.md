# QuickPickr — Market Requirements Document (MRD)

| Field | Value |
|-------|-------|
| **Product** | QuickPickr — Quick-Commerce Price Comparison (India) |
| **Version** | 1.1 |
| **Date** | 2026-05-19 |
| **Author** | @product-mgr |
| **Status** | Draft for stakeholder review |
| **Companion** | [prd.md](./prd.md), [context-summary.md](./context-summary.md) |

---

## 1. Executive Summary

Indian quick-commerce has consolidated around four national platforms—**Blinkit**, **Zepto**, **BigBasket** (quick delivery), and **Swiggy Instamart**—promising 10–30 minute delivery of groceries and household essentials in 150+ cities. Pricing is volatile: the same branded SKU often differs by **10–40%** across apps on the same day due to promotions, dynamic pricing, and zone-level inventory.

Today, a price-conscious shopper who wants the best deal on a single item (e.g., *Amul Gold 500 ml*) must **open four apps**, search in each, scroll past sponsored listings, mentally normalize pack sizes, and compare manually—a **2–5 minute** ritual per item that does not scale to a full basket. Most shoppers stop after one or two apps and pay an unobserved premium.

**QuickPickr** is a search-first comparison layer: the shopper enters a product name and pincode once; the product queries a **Vertex AI Search** index of the four retailer websites, extracts INR prices from returned snippets, and shows **one price-ranked table** with deep links to each retailer’s product page. Purchase, payment, and fulfillment remain on the retailer’s platform.

**Core value proposition:** one search instead of four—a **~30 second** price check instead of a multi-app hunt—while preserving trust and checkout on the retailer the shopper already uses.

---

## 2. Market Opportunity

### 2.1 Market size and growth

| Metric | Estimate | Notes |
|--------|----------|-------|
| India quick-commerce GTV (2025) | ~₹33,000 Cr (~USD 6.8B) | Industry reports, FY25 run-rate |
| Historical CAGR (2020–2024) | ~71% | Hyper-growth phase |
| Projected CAGR (2025–2029) | ~17–18% | Maturing but still expanding |
| Monthly users (sector) | 33M+ | Across major platforms |
| Dark stores (mapped) | 20,000+ | Metro-heavy footprint |

**Implication:** The category is large enough to support utility-style discovery products with high repeat frequency (daily/weekly staples), not just occasional travel-style comparison.

### 2.2 Structural opportunity: price dispersion + multi-homing

1. **Persistent price dispersion** — Identical SKUs routinely show double-digit percentage gaps within the same neighborhood; promotions rotate independently per platform.
2. **Multi-homing is normative** — A majority of frequent quick-commerce users maintain **two or more** apps; switching is already accepted behavior.
3. **No category-native comparator** — Flight (Ixigo), hotels (MakeMyTrip), and general e-commerce (BuyHatke, Trackr) have comparison products; **quick-commerce groceries lack an equivalent** despite higher purchase frequency.

### 2.3 Addressable use case

| Segment | Description | QuickPickr fit |
|---------|-------------|----------------|
| **Primary** | Urban tier-1/2 households, 3–5+ quick-commerce orders/week | High — staples price checks |
| **Secondary** | Deal-driven solo shoppers, promo-sensitive | Medium — “cheapest today” |
| **Tertiary** | Household planners optimizing weekly spend | High — planning, repeat searches |

**Serviceable obtainable market (directional):** Even 1–2% of monthly quick-commerce users adopting a free comparison utility yields **300K–600K MAU** at sector scale—sufficient for affiliate/sponsored monetization and partnership conversations.

---

## 3. Target Users and Personas

### 3.1 Primary — Priya, 32, Bengaluru

| Attribute | Detail |
|-----------|--------|
| **Behavior** | Orders groceries 3–5×/week via quick-commerce |
| **Apps** | Blinkit, Zepto, Instamart installed |
| **Sensitivity** | Branded staples (milk, atta, oil, snacks)—knows “fair” price ±₹10 |
| **Pain** | Checks 2 apps manually; suspects she still overpays |
| **Success** | One search → ranked table → tap cheapest → buy on retailer app |

### 3.2 Secondary — Rohan, 26, Mumbai

| Attribute | Detail |
|-----------|--------|
| **Behavior** | Deal-driven; opens app with best banner |
| **Pain** | No single view of “who is cheapest today” |
| **Success** | Fast answer before committing to an app for the order |

### 3.3 Tertiary — Meera, 48, Delhi

| Attribute | Detail |
|-----------|--------|
| **Behavior** | Family of four; splits basket across apps for cost |
| **Pain** | High friction comparing many items |
| **Success** | QuickPickr as planning tool for high-value single-SKU checks (v1); basket later (v2+) |

### 3.4 Shared job-to-be-done

> *When I need to buy a known grocery item, help me find the cheapest available price across the apps I already use, in under a minute, without making me leave the retailer’s checkout I trust.*

---

## 4. User Stories (Structured Format)

Each story uses a consistent schema for traceability into the PRD. **Priority:** P0 = must-have for market entry; P1 = strengthens adoption; P2 = future.

### 4.1 Story schema

| Field | Description |
|-------|-------------|
| **ID** | Unique identifier (US-MRD-###) |
| **Epic** | Themed capability group |
| **Persona** | Primary user the story serves |
| **Story** | As a / I want / So that |
| **Acceptance criteria** | Observable outcomes that signal success |
| **Priority** | P0 \| P1 \| P2 |
| **Trust sensitivity** | Low \| Medium \| High — how much user trust is at stake if we fail |

---

### US-MRD-001 — Single search across four apps

| Field | Value |
|-------|-------|
| **ID** | US-MRD-001 |
| **Epic** | E1 — Compare prices |
| **Persona** | Priya (Primary) |
| **Story** | **As a** price-conscious shopper, **I want to** enter one product name and my pincode and see prices from Blinkit, Zepto, BigBasket, and Instamart in one place, **so that** I do not have to open four separate apps. |
| **Acceptance criteria** | (1) One query returns up to four retailer rows. (2) User completes input in under 15 seconds. (3) Time from submit to first visible price is under 30 seconds perceived (product target ~30s end-to-end). |
| **Priority** | P0 |
| **Trust sensitivity** | High |

---

### US-MRD-002 — Cheapest option is obvious

| Field | Value |
|-------|-------|
| **ID** | US-MRD-002 |
| **Epic** | E1 — Compare prices |
| **Persona** | Priya, Rohan |
| **Story** | **As a** shopper comparing staples, **I want to** see results ranked from lowest to highest price, **so that** I can identify the cheapest option without mental math. |
| **Acceptance criteria** | (1) Default sort is ascending by displayed INR price. (2) Cheapest row is explicitly labeled (not color-only). (3) User can explain why row #1 is cheapest in under 5 seconds. |
| **Priority** | P0 |
| **Trust sensitivity** | High |

---

### US-MRD-003 — Buy on the retailer I trust

| Field | Value |
|-------|-------|
| **ID** | US-MRD-003 |
| **Epic** | E2 — Complete purchase on retailer |
| **Persona** | Priya, Meera |
| **Story** | **As a** shopper who has chosen the best price, **I want to** tap once and land on that retailer’s product page, **so that** I can check out on a platform I already trust without searching again. |
| **Acceptance criteria** | (1) Each available row has a clear “Buy on [Retailer]” action. (2) Click-out opens the matched SKU page, not home or search. (3) Payment and delivery remain entirely on the retailer. |
| **Priority** | P0 |
| **Trust sensitivity** | High |

---

### US-MRD-004 — Know when a retailer does not have the item

| Field | Value |
|-------|-------|
| **ID** | US-MRD-004 |
| **Epic** | E1 — Compare prices |
| **Persona** | Rohan |
| **Story** | **As a** deal-driven shopper, **I want to** see which apps do not carry the item at my pincode, **so that** I know the comparison is complete and I am not missing a hidden cheaper option. |
| **Acceptance criteria** | (1) Missing retailers appear as rows with “Not available at your pincode” (not omitted). (2) User does not assume the app only searched one retailer. |
| **Priority** | P0 |
| **Trust sensitivity** | Medium |

---

### US-MRD-005 — Compare the same product, not a lookalike

| Field | Value |
|-------|-------|
| **ID** | US-MRD-005 |
| **Epic** | E3 — Trustworthy comparison |
| **Persona** | Priya, Meera |
| **Story** | **As a** shopper who knows what I want to buy, **I want to** see product title and pack size on every row, **so that** I am comparing like-for-like SKUs and not a cheaper substitute. |
| **Acceptance criteria** | (1) Each row shows title + pack size. (2) Uncertain matches are labeled “Closest match.” (3) User can spot a pack-size mismatch without opening retailer apps. |
| **Priority** | P0 |
| **Trust sensitivity** | High |

---

### US-MRD-006 — Believe the price is current

| Field | Value |
|-------|-------|
| **ID** | US-MRD-006 |
| **Epic** | E3 — Trustworthy comparison |
| **Persona** | Priya |
| **Story** | **As a** shopper who has been burned by outdated deals before, **I want to** see when each price was last updated, **so that** I can decide whether to trust the comparison before I switch apps. |
| **Acceptance criteria** | (1) Every price row shows a freshness indicator (e.g., “Updated 2 min ago”). (2) Stale prices (>5 min) are visually distinct or labeled. (3) User survey: ≥70% agree “I understand how fresh this price is” (beta). |
| **Priority** | P0 |
| **Trust sensitivity** | High |

---

### US-MRD-007 — Pincode without repeat typing

| Field | Value |
|-------|-------|
| **ID** | US-MRD-007 |
| **Epic** | E4 — Convenience |
| **Persona** | Priya, Meera |
| **Story** | **As a** returning shopper, **I want** my pincode remembered on this device, **so that** repeat price checks take even less effort. |
| **Acceptance criteria** | (1) After first valid pincode entry, field is prefilled on next visit. (2) User can change pincode before each search. (3) Pincode is not required to create an account. |
| **Priority** | P0 |
| **Trust sensitivity** | Low |

---

### US-MRD-008 — Quick check before placing an order

| Field | Value |
|-------|-------|
| **ID** | US-MRD-008 |
| **Epic** | E4 — Convenience |
| **Persona** | Rohan |
| **Story** | **As a** shopper about to place an order in one app, **I want to** quickly verify if another app is cheaper today, **so that** I do not regret overpaying on a high-frequency item. |
| **Acceptance criteria** | (1) Median successful comparison completes in under 60 seconds wall-clock. (2) User reports “saved time vs opening all apps” in beta interviews (majority agree). |
| **Priority** | P0 |
| **Trust sensitivity** | Medium |

---

### US-MRD-009 — Plan a high-value staple purchase (P1)

| Field | Value |
|-------|-------|
| **ID** | US-MRD-009 |
| **Epic** | E4 — Convenience |
| **Persona** | Meera (Tertiary) |
| **Story** | **As a** household planner, **I want to** re-run recent searches from history, **so that** I can re-check prices on weekly staples without retyping product names. |
| **Acceptance criteria** | (1) Last 20 searches are listed locally. (2) One tap re-runs search with current index data. |
| **Priority** | P1 |
| **Trust sensitivity** | Low |

---

### 4.2 Epic summary

| Epic | Stories | P0 count |
|------|---------|----------|
| E1 — Compare prices | US-MRD-001, 002, 004 | 3 |
| E2 — Complete purchase on retailer | US-MRD-003 | 1 |
| E3 — Trustworthy comparison | US-MRD-005, 006 | 2 |
| E4 — Convenience | US-MRD-007, 008, 009 | 2 (+1 P1) |

---

## 5. User Trust Risk

User trust is the primary adoption constraint for a price comparison product that does not own checkout. If shoppers believe QuickPickr is wrong, biased, or opaque, they will revert to opening retailer apps directly—regardless of speed gains.

### 5.1 Trust risk register

| Risk ID | Trust risk (user perception) | Example failure mode | Likelihood | Impact on trust | Mitigation (product + market) |
|---------|------------------------------|----------------------|------------|-----------------|-------------------------------|
| **UTR-01** | **“The cheapest price is wrong.”** | Indexed price is stale; user sees higher price on retailer PDP | Medium | Critical | Freshness timestamps; ≤5 min target; stale label; click-out disclaimer |
| **UTR-02** | **“You compared different products.”** | 500 ml vs 1 L matched as same row | Medium | Critical | Conservative matching; “Closest match” badge; pack size on every row |
| **UTR-03** | **“You only searched one app.”** | Failed retailers hidden from UI | Low | High | Always show four rows; explicit unavailable copy |
| **UTR-04** | **“The link tricked me.”** | Deep link opens search/home, not SKU | Medium | Critical | Golden-set link QA; 100% PDP accuracy on release gate |
| **UTR-05** | **“Price changed at checkout — your fault.”** | Promo ends between index and purchase | High | Medium | CTA microcopy: “Price confirmed on [Retailer]”; no price guarantee claim |
| **UTR-06** | **“This app favors paid partners.”** | Sponsored row looks like organic cheapest | Low (v1) | Critical | No sponsored rows in v1; when added, fixed slot + “Sponsored” label |
| **UTR-07** | **“You’re selling my data.”** | Fear of pincode/search harvesting | Medium | High | No account v1; pincode local-only; public privacy policy; minimal analytics |
| **UTR-08** | **“Is this app even legitimate?”** | Unknown brand, no explanation of data source | Medium | High | Footer: “Prices sourced from retailer websites”; retailer logos; no fake urgency |
| **UTR-09** | **“Delivery fee was hidden.”** | Ranked cheapest on item price but not total landed cost | Medium | High | Show “+ delivery” when unknown; unit price where possible; PRD OQ on fee inclusion |
| **UTR-10** | **“Hindi search doesn’t work.”** | Transliterated query returns poor matches | Medium | Medium | Accept mixed-script input; Hindi UI P1; quality monitoring on Devanagari queries |

### 5.2 Trust principles (market requirements)

These principles must hold in positioning, UX, and partnerships—not only engineering:

1. **Never claim a price guarantee** — QuickPickr surfaces indexed retailer data, not live checkout quotes.
2. **Show your work** — Freshness time, retailer name, and product title/pack visible on every row.
3. **Fail visible, not silent** — Unavailable or uncertain states are explicit; never imply completeness when data is missing.
4. **Neutral rank in v1** — Cheapest by displayed rules only; monetization must not reorder organic results without disclosure.
5. **Checkout stays sacred** — All payment trust remains with Blinkit, Zepto, BigBasket, and Instamart.

### 5.3 Trust metrics (market-level)

| Metric | Target | Ties to risk |
|--------|--------|--------------|
| **Price accuracy rate** (±2% vs live retailer at click-out) | ≥98% on golden set | UTR-01 |
| **False match rate** (user-reported wrong SKU) | <2% of searches | UTR-02 |
| **Click-out success rate** (lands on intended PDP) | ≥99% | UTR-04 |
| **Trust survey** (“I trust these prices”) | ≥4.0 / 5 in beta | UTR-01, 08 |
| **Week-2 retention after first click-out** | ≥40% | Composite trust + utility |

### 5.4 Stories with highest trust sensitivity

| Story ID | Why trust is critical |
|----------|----------------------|
| US-MRD-001, 002 | Core promise is accurate multi-app comparison |
| US-MRD-003 | Broken link destroys confidence instantly |
| US-MRD-005, 006 | Wrong product or stale price = permanent churn |
| UTR-01, UTR-02, UTR-04 | Top three risks to address before public launch |

---

## 6. Problem Statement

### 6.1 Current workflow (as-is)

```mermaid
flowchart LR
  A[Need item] --> B[Open App 1]
  B --> C[Search + find price]
  C --> D[Open App 2]
  D --> E[Search + find price]
  E --> F[Open App 3]
  F --> G[Search + find price]
  G --> H[Open App 4]
  H --> I[Search + find price]
  I --> J[Mental compare]
  J --> K[Buy on one app]
```

**Pain points:**

| Pain | Impact |
|------|--------|
| Repetitive search across 4 UIs | 2–5 min per item |
| Sponsored/noisy results | Wrong SKU, wrong pack size |
| Pack-size mismatch | Apples-to-oranges comparison |
| Pincode/serviceability hidden until late | Wasted effort |
| No memory of “who was cheapest last time” | Repeat friction |

### 6.2 Desired workflow (to-be)

```mermaid
flowchart LR
  A[Need item] --> B[Open QuickPickr]
  B --> C[Product + pincode]
  C --> D[Ranked table]
  D --> E[Tap cheapest CTA]
  E --> F[Retailer product page]
  F --> G[Checkout on retailer]
```

**Target time-to-decision:** ~30 seconds for a confident single-SKU comparison.

---

## 7. Solution Concept and Value Proposition

### 7.1 What QuickPickr is

- A **discovery and comparison** product—not a marketplace, cart, or payment processor.
- **Indexed search** over public retailer catalog surfaces (Vertex AI Search).
- **Price extraction** from search snippets + structured fields (INR parsing).
- **Neutral ranking** by price (v1), with clear retailer attribution.

### 7.2 What QuickPickr is not (v1)

- In-app checkout, cart, or inventory ownership
- Basket optimization across retailers
- Loyalty, coupons, or subscription management
- Categories beyond grocery/household essentials on the four named retailers

### 7.3 Value pillars

| Pillar | User benefit | Business benefit |
|--------|--------------|------------------|
| **Speed** | One search vs four | High repeat sessions |
| **Trust** | Buy on retailer platform | Lower regulatory/commerce burden |
| **Transparency** | Source-attributed prices | Defensible vs dark patterns |
| **Coverage** | Four major platforms | Category completeness story |

---

## 8. Competitive Landscape

### 8.1 Landscape map

| Category | Examples | Quick-commerce grocery comparison? |
|----------|----------|-----------------------------------|
| **Quick-commerce apps** | Blinkit, Zepto, BigBasket, Instamart | No — single-catalog only |
| **General e-commerce comparators** | BuyHatke, PriceDekho, Trackr | No — Amazon/Flipkart focus; weak pincode/q-commerce |
| **Manual/social** | WhatsApp groups, Reddit | Demand signal only — not scalable |
| **Direct competitor** | — | **White space today** |

### 8.2 Competitive matrix (illustrative)

| Capability | QuickPickr (target) | Retailer apps | BuyHatke-class |
|------------|---------------------|---------------|----------------|
| 4-way q-commerce coverage | Yes | No | No |
| Pincode-aware pricing | Yes | Yes (own only) | Partial |
| Single-query comparison | Yes | No | Partial (non-q-commerce) |
| Deep link to SKU | Yes | N/A | Varies |
| Real-time freshness (<5 min) | Target 95% | Live | Varies |

### 8.3 Defensibility

Moat is **data freshness + breadth + SKU matching quality** across four fast-changing sites—not retailer partnerships alone (though partnerships improve sustainability).

---

## 9. Business Model and Monetization

### 9.1 Launch posture (v1)

- **Free to use**; minimal ads; no account required.
- Optimize for **habit formation** and click-out volume.

### 9.2 Monetization paths (post-traction)

| Stream | Mechanism | Timing |
|--------|-----------|--------|
| **Affiliate / referral** | Tagged deep links per retailer | When programs available |
| **Sponsored placement** | Clearly labeled rows (never conflate with organic rank) | After trust established |
| **Insights (B2B)** | Aggregated demand/price index (anonymized) | Scale phase |

### 9.3 Unit economics considerations

- Primary variable cost: **Vertex AI Search + crawl/index** at query volume.
- Mitigation: query caching, index refresh tiering, budget alerts.

---

## 10. Go-to-Market Strategy

### 10.1 Launch geography

- **Phase 1 cities:** Bengaluru, Mumbai, Delhi NCR, Hyderabad, Pune (highest q-commerce density).
- Pincode validation and serviceability messaging tuned per city.

### 10.2 Acquisition channels

| Channel | Tactic |
|---------|--------|
| **Organic / SEO** | “[product] price Blinkit Zepto” landing patterns |
| **Community** | Reddit, Twitter/X, local deal groups |
| **Word of mouth** | “Check QuickPickr before you order” habit |
| **Partnerships** | Affiliate conversations with retailers (non-blocking for launch) |

### 10.3 Positioning statement

**For** Indian shoppers who use multiple quick-commerce apps, **QuickPickr** is the fastest way to **see who has the lowest price** on a grocery item at your pincode—**so you can buy where you already shop**, in seconds.

---

## 11. Success Metrics and KPIs

### 11.1 North-star metric

**Weekly successful comparisons** — searches that return ≥3 retailer rows and generate ≥1 click-out within 7 days.

### 11.2 Adoption (12-month targets — directional)

| Metric | Target |
|--------|--------|
| Installs | 500,000 |
| MAU | 150,000 |
| D30 retention | >35% |

### 11.3 Engagement

| Metric | Target |
|--------|--------|
| Searches per WAU | ≥5 |
| Click-through to retailer | ≥60% of result views |
| Median time-to-first-result | <1.5s P50 |

### 11.4 Quality (non-negotiable)

| Metric | Target |
|--------|--------|
| Price freshness (≤5 min old) | ≥95% of displayed rows |
| Top-500 SKU coverage (≥3/4 retailers) | ≥90% of queries in launch cities |

---

## 12. Regulatory, Legal, and Compliance

| Area | Consideration |
|------|----------------|
| **DPDP Act (India)** | Minimize PII; pincode local-only in v1; public privacy notice |
| **Consumer protection** | Clear attribution; no misleading “lowest” without freshness |
| **Platform ToS / scraping** | Public pages; robots.txt compliance; partnership path |
| **Comparison engine norms** | Neutral presentation; sponsored disclosure when added |

---

## 13. Business and Technical Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Retailer C&D on indexing | High | Public data only; attribution; affiliate outreach |
| Site structure breaks parsers | High | Parse-failure alarms; on-call playbook |
| Stale prices erode trust | High | See §5 User Trust Risk (UTR-01); freshness labels; stale-row policy |
| Retailers clone feature | Medium | Weak incentive to show competitor prices |
| Vertex AI cost at scale | Medium | Caching, rate limits, spend caps |
| False SKU matching | High | See §5 User Trust Risk (UTR-02); “closest match” labels |
| User trust collapse (composite) | High | Trust principles §5.2; trust metrics §5.3; ship only when golden-set passes |

---

## 14. Product Roadmap (Market View)

| Phase | Horizon | Market theme |
|-------|---------|--------------|
| **MVP** | 0–3 mo | Single-SKU search, 4 retailers, web + mobile |
| **v1.1** | 3–6 mo | History, Hindi UI, improved matching |
| **v2** | 6–12 mo | Multi-item basket compare, delivery-time dimension |
| **v3** | 12+ mo | Alerts, price-drop notifications, more retailers |

---

## 15. Out of Scope for v1 (Market)

- Checkout, cart, payments, returns
- Multi-retailer basket optimization
- Non-grocery categories (electronics, fashion)
- Retailers beyond Blinkit, Zepto, BigBasket, Swiggy Instamart
- Loyalty / coupon stacking
- Personalized “deals for you” feeds

---

## Sources

| # | Source | Use |
|---|--------|-----|
| 1 | Research and Markets — India Quick Commerce Market (Q1 2026 databook) | Market size, CAGR |
| 2 | Ken Research — India Quick Commerce Strategic POV 2025 | Growth drivers |
| 3 | Business Standard — Quick commerce reshapes retail 2025 | Sector trends, user scale |
| 4 | NDTV Profit / industry share reports — Blinkit ~44%, Zepto ~30%, Instamart ~23% FY25 | Competitive shares |
| 5 | Stakeholder brief — QuickPickr use case (2026-05-19) | Problem, workflow, Vertex AI Search approach |
| 6 | Adjacent comparators — Ixigo, MakeMyTrip, BuyHatke (public positioning) | Category precedent |

---

## Assumptions

1. Publicly accessible retailer product pages can be indexed within robots.txt and legal constraints for an MVP.
2. Vertex AI Search returns snippets sufficient for INR price extraction with acceptable accuracy after tuning.
3. Shoppers will tolerate opening retailer apps/sites for checkout if discovery saves meaningful time.
4. Four-retailer coverage is sufficient for perceived completeness in launch cities.
5. Pincode is an adequate proxy for serviceability vs lat/long geofencing in v1.
6. Market size figures are directional for planning, not investment-grade forecasts.

---

## Open Questions

1. Which retailer affiliate programs are available at launch, and what attribution windows apply?
2. Should BigBasket “quick” vs scheduled delivery SKUs be distinguished in comparison rows?
3. Is there regulatory guidance in India specific to price comparison engines beyond DPDP?
4. What is the acceptable stale-price UX when index lag exceeds 5 minutes—show with label vs hide?
5. Priority cities for crawl freshness investment beyond tier-1 five?

---

## Audit

| Timestamp (UTC) | Persona | Action |
|-----------------|---------|--------|
| 2026-05-19T00:00:00Z | @product-mgr | Initial comprehensive MRD authored from stakeholder brief and market research synthesis |
| 2026-05-19T12:00:00Z | @product-mgr | Added §4 User Stories (structured format) and §5 User Trust Risk; renumbered subsequent sections |
