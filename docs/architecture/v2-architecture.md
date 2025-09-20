# Architecture v2 — Event Builder Platform

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/04-auth-rbac.md`, `docs/shards/05-devops-migrations.md`
ADR refs: `docs/adr/ADR-001-PartnerOfRecord-and-Commissions.md`, `docs/adr/ADR-002-DomainClaims-Email-Verification.md`, `docs/adr/ADR-003-Entitlements-and-PricingLayers.md`, `docs/adr/ADR-004-Consumption-Metering-and-Pricing.md`, `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`

## 1) Data Contracts (DDL-oriented)

### 1.1 Tenancy & Identity (recap)
- `organization`: `org_id uuid pk`, `legal_name`, `org_slug unique`, `billing_email`, `default_timezone`, `tax_id?`, `visibility ENUM('private','partners','public') default 'private'`.
- `user`: `user_id uuid pk`, `email citext unique`, `default_org_id uuid null`.
- `membership`: `org_id`, `user_id`, `role ENUM('Admin','User')`, `status ENUM('active','pending')`, `PRIMARY KEY(org_id, user_id)`.

### 1.2 Domain Claims (email-based)
- `domain_claim`: `claim_id uuid pk`, `org_id fk`, `domain citext`, `status ENUM('pending','verified','revoked','pending_conflict')`, `verified_at timestamptz null`, `wildcard bool default false`, `proof jsonb`, `UNIQUE(domain) WHERE status IN ('pending','verified')`.
- `invitation` (augment): `UNIQUE(org_id, lower(email)) WHERE consumed_at IS NULL`.

### 1.3 Channel & Commissions
- `partner_of_record`: `org_id`, `partner_id`, `start_at`, `end_at null`, `status ENUM('active','expired','disputed')`, `PRIMARY KEY(org_id, partner_id, start_at)`.
- `commission_rate`: `partner_tier`, `sku`, `pct numeric(5,2)`.
- `ledger`: `entry_id`, `org_id`, `project_id?`, `sku`, `quantity`, `amount_gross`, `partner_pct`, `partner_amount`, `net`, `status ENUM('pending','settled','reversed')`, `created_at`.

### 1.4 Business Models & Entitlements
- `business_model`: `model_id`, `code unique`, `name`, `status`, `version`, `currency`, `default_plan_id`.
- `plan`: `plan_id`, `model_id fk`, `name`, `tier`, `status`, `notes`.
- `product_sku`: `sku pk`, `type ENUM('hosting','object','validation','action','analytics')`, `unit`, `cost`, `retail`, `tax_code`, `metadata jsonb`.
- `plan_sku`: `plan_id fk`, `sku fk`, `included_qty numeric`, `overage_price numeric`, `tiers jsonb`, `PRIMARY KEY(plan_id, sku)`.
- `org_entitlement`: `org_id fk`, `plan_id fk`, `overrides jsonb`, `effective_at`, `PRIMARY KEY(org_id, plan_id)`.
- `org_business_model`: `org_id fk`, `model_id fk`, `plan_id fk`, `assigned_by`, `assigned_at`, `notes`.

### 1.5 Metering & Estimates
- `metering_event`: `event_id uuid pk`, `org_id`, `project_id`, `sku`, `quantity numeric`, `source ENUM('form_submit','backend','replay')`, `event_time`, `request_id unique`, `metadata jsonb`.
- `pricing_estimate` (cache): `estimate_id`, `org_id`, `project_id`, `inputs jsonb`, `result jsonb`, `created_at`.

### 1.6 Auditing
- All writes to `domain_claim`, `org_business_model`, `plan_sku`, `org_entitlement`, `commission_rate` produce audit entries with actor and before/after JSON.

### 1.7 Group Hierarchy & Billing Accounts (enterprise)
- `organization` (augment): add `parent_org_id uuid null`; if set, parent must exist.
- `org_hierarchy` (closure table): `ancestor_org_id uuid`, `descendant_org_id uuid`, `depth int`, `PRIMARY KEY(ancestor_org_id, descendant_org_id)`.
- `billing_account`: `billing_account_id uuid pk`, `owner_org_id uuid fk`, `name`, `currency`, `status`, `notes`.
- `org_billing_mapping`: `org_id uuid fk`, `billing_account_id uuid fk`, `allocation ENUM('absorb','chargeback','split')`, `percent numeric(5,2) null`, `effective_at timestamptz`, `PRIMARY KEY(org_id, billing_account_id, effective_at)`.
- `cost_center` (optional): `cost_center_id pk`, `billing_account_id fk`, `code`, `name`.
- `project` (augment): `cost_center_id uuid null`.
- `group_role_membership`: `ancestor_org_id`, `user_id`, `role ENUM('GroupAdmin','GroupBilling','GroupSupport')`, `PRIMARY KEY(ancestor_org_id, user_id)`.
- PoR precedence: if a `billing_account` has a PoR, it overrides sub‑org PoRs for consolidated lines; else fallback to the line’s `org_id` PoR.

## 2) Services & API Contracts

### 2.1 Service Map
- Auth/Identity Service: sessions, memberships, org context.
- Domain Verification Service: token issuance, inbound email processing, DKIM/SPF/DMARC validation, conflict workflow.
- Catalog/Entitlements Service: manages `product_sku`, `plan_sku`, `org_entitlement`, `org_business_model`.
- Metering Ingest: idempotent event collector (`request_id`), durable queue, replay.
- Pricing Engine: computes charges per event/rollup; tiered pricing; currency rounding; tax codes.
- Ledger/Settlement: writes `ledger` lines; applies PoR commission; real‑time payouts (threshold) and weekly sweeps; refunds via reverse entries.
- Estimator API: deterministic previews using same pricing rules as engine; cached.

### 2.2 Selected Endpoint Contracts
- `POST /verify/email-submit` → `{ token, from_domain, dkim_pass, spf_pass, dmarc_aligned }` → `200 {status}`.
- `POST /metering/events` (batch) → `[{request_id, sku, quantity, org_id, project_id, time}]` → `202` on enqueue.
- `POST /pricing/estimate` → `{org_id, project_id, skus:{sku: uses_per_lead}, leads}` → `{ base, lines:[{sku, included, overage, total}], grand_total }`.
- `POST /billing/charges` → pricing → ledger lines (with PoR split).
- Group/Hierarchy endpoints: see `docs/architecture/group-billing-and-hierarchy-apis.md`.
- Mutations (enterprise):
  - `POST /orgs/{id}/children` (create child or link existing)
  - `POST /billing-accounts` (create), `POST /billing-accounts/{id}/map-org` (mapping)
  - `POST /groups/{ancestor_org_id}/roles` (add GroupAdmin/Support/Billing)
  - `POST /assist-sessions` (start with purpose), `POST /assist-sessions/{id}:end`

## 3) Non‑Functional Requirements
- Idempotency: `request_id` enforced at metering ingest; pricing safe to replay.
- Consistency: eventual consistency tolerated; nightly reconciliation against provider logs (SMS/email).
- Scalability: queue‑backed ingest; per‑org partitions; shard ledger tables by month.
- Resilience: provider abstractions; fallback queues; dead‑letter with replay.
- Cost Guardrails: budgets/caps enforced at engine and at action initiation.
- Security: least privilege; signed webhooks; PII minimization in events; role‑based model assignment.

## 4) Risks & Mitigations
- Metering drift ↔ nightly reconciliation + anomaly alerts.
- Email spoofing ↔ DMARC alignment & header capture hashed into `proof`.
- Partner disputes ↔ PoR rules + audit + dispute tooling.
- Cost spikes ↔ budgets, caps, and prepaid credits for SMS/validations.

## 5) Migration Plan (Alembic Order)
1. `20250920_01_domain_claims_email.py`
2. `20250920_02_por_commission_ledger.py`
3. `20250920_03_business_model_entitlements.py`
4. `20250920_04_metering_events.py`
5. `20250920_05_org_hierarchy_and_billing_accounts.py` — adds hierarchy + billing account tables and mappings; backfill roots; default billing account per root.

- Rollback: each migration includes reversible DDL and safe data downgrades.
- Config: real‑time PoR split threshold default `AUD 50` per ledger line (configurable).

## 6) Change Log
### 2025-09-20 — v2 Reset
- Adds domain_claims, PoR/ledger, business_model/entitlements, metering_events contracts.
- Establishes services for Domain Verification, Catalog/Entitlements, Metering, Pricing, Ledger/Settlement, Estimator.
- Defines NFRs and risk mitigations per v2 baseline.
