# PRD v2 — Event Builder Platform

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/01-builder-ux.md`, `docs/shards/02-data-schema.md`, `docs/shards/03-billing-go-live.md`, `docs/shards/04-auth-rbac.md`, `docs/shards/05-devops-migrations.md`
ADR refs: `docs/adr/ADR-001-PartnerOfRecord-and-Commissions.md`, `docs/adr/ADR-002-DomainClaims-Email-Verification.md`, `docs/adr/ADR-003-Entitlements-and-PricingLayers.md`, `docs/adr/ADR-004-Consumption-Metering-and-Pricing.md`, `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`

## 2025-09-20 — v2 Reset
- Business models: Direct Day-Pass, Consumption (Base + SKUs), Reseller/Wholesale; per-org assignment.
- Channel: Platform-owned + Partner-of-Record; real-time ≥ threshold + weekly sweep; deal reg & referral codes.
- Privacy & Discovery: P1 Private Suggestions; P2 Partner Directory (later); no member identity leakage.
- Domain Claims: Email-based, multi-domain, DMARC-aligned; wildcard guardrails; conflict workflow.
- Entitlements & SKU catalog: Hosting/Object/Validation/Action/Analytics; included/overage/tiers.
- Consumption billing: builder estimator (100-lead default), budgets/caps/alerts.
- Enterprise: multi-org hierarchy, group billing & Head Office dashboard, Assist Mode with audit.

---

## Business Models & Assignment (Direct, Consumption, Reseller)
- Supported concurrently per organization: Direct Day‑Pass (retail), Consumption (Base Pack + SKUs), Reseller/Wholesale.
- Per‑org assignment via `org_business_model(model_id, plan_id, assigned_by, assigned_at)` with audit; default plan per model.
- Plans define included quantities and overage pricing per SKU; org‑level overrides via `org_entitlement(overrides jsonb)`.
- Reference: ADR‑003; Shards: 02‑data‑schema, 03‑billing‑go‑live.

## Channel Model & Commissions (Platform‑owned + PoR)
- Platform‑owned channel with Partner‑of‑Record default when present.
- Settlement:
  - Real‑time commission split for ledger lines with gross amount ≥ configured threshold (default AUD $50).
  - Weekly sweep for smaller lines; disputes supported via reversible ledger entries.
- Deal registration and referral codes supported; PoR status lifecycle with audit.
- Reference: ADR‑001; Shard: 02‑data‑schema.

## Privacy & Discovery
- Private‑by‑default. P1: Private Suggestions now; P2: Partner Directory later.
- No member identity leakage; privacy‑safe hints with CTA to Join Request.
- Directory visibility toggles; domain claims and invites never reveal member lists.
- References: ADR‑002; Shards: 01‑builder‑ux, 04‑auth‑rbac.

## Domain Claims (Email‑based)
- Email‑based domain verification aligned with DMARC; store proof (hashed headers) in `domain_claim.proof`.
- Multi‑domain per org; `status ∈ {pending, verified, revoked, pending_conflict}`; wildcard allowed only post root verify with Owner + 2FA.
- Conflict workflow supported; invitations enforce uniqueness `UNIQUE(org_id, lower(email)) WHERE consumed_at IS NULL`.
- Reference: ADR‑002; Shards: 02‑data‑schema, 04‑auth‑rbac.

## Entitlements & SKU Catalog
- SKU types: Hosting, Object, Validation, Action, Analytics.
- `product_sku` defines unit/cost/retail/tax_code; `plan_sku` sets `included_qty`, `overage_price`, optional tier ladder `tiers jsonb`.
- Org entitlements via `org_entitlement`; assignment via `org_business_model`.
- References: ADR‑003; Shards: 02‑data‑schema, 03‑billing‑go‑live.

## Consumption Billing & Estimator
- Estimator in Builder right rail: 100‑lead default, slider (10 → 10k), per‑SKU lines with included vs overage and total.
- Prepaid warnings for SMS/validations; budgets/caps with alerts at 50/80/100%.
- Estimator uses same pricing rules as engine; deterministic and cached.
- References: ADR‑004; Shards: 03‑billing‑go‑live.

## Enterprise Multi‑Org & Group Billing UX
- Head Office Dashboard UX is an incorporated section (see shard): information architecture, wireframes (Overview, Billing, Subsidiary, Assist, Model Assignment, Budgets, Domains), copy & states, accessibility, telemetry, and acceptance criteria.
- Cross‑link ACs to relevant stories (auth/invite, domains, budgets, billing visibility).
- References: ADR‑005; Shards: 01‑builder‑ux.
- See: `docs/prd/enterprise-multi-org-and-group-billing.md` and `docs/front-end-spec/head-office-dashboard.md`.
- Allocation strategies (billing accounts): absorb, chargeback, split (%). Consolidation locus = billing_account; invoices pull lines for mapped orgs during period.
- Entitlements inheritance: billing_account may define default plan + SKU overrides that children inherit unless explicitly overridden.
- PoR precedence: PoR at billing_account overrides child org PoRs for those consolidated lines.
- Group domain delegation: head office can verify corporate domains and delegate sub‑domains to subsidiaries (store delegation list in claim `proof`).

## Success Metrics
- Domain claim verification median time.
- % of signups routed to Join Requests (privacy‑safe hints effectiveness).
- % partner‑sourced revenue and commission payout accuracy.
- Variable validation costs covered by pricing (gross margin target).
- Dispute SLA: creation → resolution time within target percentile.

---

## Cross‑References
- Architecture v2: `docs/architecture/v2-architecture.md`
- Front‑End Spec v2: `docs/front-end-spec/v2-front-end-spec.md`
- ADRs: 001–005 listed above

