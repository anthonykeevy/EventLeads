# Restart v2 Master Spec & Execution — Event Builder

This single source consolidates **all details** agreed in our sessions (business models, privacy, channel, domain claims, consumption billing) plus **Architect & UX deep feedback**. It also provides **full, copy‑ready prompts** for PM, Architect, UX, SM, and PO, and a **runbook** for you. Use this instead of addenda; this is the **v2 baseline**.

---

## 0) Scope at a Glance (What v2 includes)

* **Business Models** supported concurrently (per‑org assignment):

  * **Direct Day‑Pass (Retail)** — current model.
  * **Consumption (Base Pack + SKUs)** — objects/validations/actions metered per lead/action.
  * **Reseller/Wholesale** — agency pays wholesale or receives rev‑share (PoR).
* **Channel Economics**: Platform‑owned + **Partner‑of‑Record (PoR)** default; real‑time commission ≥ threshold + weekly sweep; deal registration & referral codes.
* **Privacy & Discovery**: Private‑by‑default; **P1 Private Suggestions** now; **P2 Partner Directory** later; no member identity leakage.
* **Domain Claims**: Multi‑domain + **email‑based verification with DMARC alignment**; optional wildcards with guardrails; conflict escalation.
* **Entitlements & Pricing**: SKU catalog (Hosting/Object/Validation/Action/Analytics), plans, per‑org overrides; budgets/caps/alerts.
* **Estimator**: In Form Builder; 100‑lead default; slider + per‑SKU breakdown; prepaid warnings.
* **Audit & Compliance**: Full auditing on claims, model assignment, pricing changes; APPs‑aligned posture; NDB readiness.

---

## 1) Detailed Data Contracts (DDL‑oriented specification)

### 1.1 Tenancy & Identity (recap)

* **organization**: `org_id uuid pk`, `legal_name`, `org_slug unique`, `billing_email`, `default_timezone`, `tax_id?`, `visibility ENUM('private','partners','public') default 'private'`.
* **user**: `user_id uuid pk`, `email citext unique`, `default_org_id uuid null`.
* **membership**: `org_id`, `user_id`, `role ENUM('Admin','User')`, `status ENUM('active','pending')`, `PRIMARY KEY(org_id, user_id)`.

### 1.2 Domain Claims (email‑based)

* **domain\_claim**: `claim_id uuid pk`, `org_id fk`, `domain citext`, `status ENUM('pending','verified','revoked','pending_conflict')`, `verified_at timestamptz null`, `wildcard bool default false`, `proof jsonb`, `UNIQUE(domain) WHERE status IN ('pending','verified')`.
* **invitation** (augment): add `UNIQUE(org_id, lower(email)) WHERE consumed_at IS NULL`.

### 1.3 Channel & Commissions

* **partner\_of\_record**: `org_id`, `partner_id`, `start_at`, `end_at null`, `status ENUM('active','expired','disputed')`, `PRIMARY KEY(org_id, partner_id, start_at)`.
* **commission\_rate**: `partner_tier`, `sku`, `pct numeric(5,2)`.
* **ledger**: `entry_id`, `org_id`, `project_id?`, `sku`, `quantity`, `amount_gross`, `partner_pct`, `partner_amount`, `net`, `status ENUM('pending','settled','reversed')`, `created_at`.

### 1.4 Business Models & Entitlements

* **business\_model**: `model_id`, `code unique`, `name`, `status`, `version`, `currency`, `default_plan_id`.
* **plan**: `plan_id`, `model_id fk`, `name`, `tier`, `status`, `notes`.
* **product\_sku**: `sku pk`, `type ENUM('hosting','object','validation','action','analytics')`, `unit`, `cost`, `retail`, `tax_code`, `metadata jsonb`.
* **plan\_sku**: `plan_id fk`, `sku fk`, `included_qty numeric`, `overage_price numeric`, `tiers jsonb`, `PRIMARY KEY(plan_id, sku)`.
* **org\_entitlement**: `org_id fk`, `plan_id fk`, `overrides jsonb`, `effective_at`, `PRIMARY KEY(org_id, plan_id)`.
* **org\_business\_model**: `org_id fk`, `model_id fk`, `plan_id fk`, `assigned_by`, `assigned_at`, `notes`.

### 1.5 Metering & Estimates

* **metering\_event**: `event_id uuid pk`, `org_id`, `project_id`, `sku`, `quantity numeric`, `source ENUM('form_submit','backend','replay')`, `event_time`, `request_id unique`, `metadata jsonb`.
* **pricing\_estimate** (cache): `estimate_id`, `org_id`, `project_id`, `inputs jsonb`, `result jsonb`, `created_at`.

### 1.6 Auditing

* All writes to `domain_claim`, `org_business_model`, `plan_sku`, `org_entitlement`, `commission_rate` produce audit entries with actor, before/after JSON.

---

## 2) Service Architecture (Architect Deep Feedback)

### 2.1 Service Map

* **Auth/Identity Service**: sessions, memberships, org context.
* **Domain Verification Service**: handles token issuance, inbound email processing, DKIM/SPF/DMARC validation, conflict workflow.
* **Catalog/Entitlements Service**: manages `product_sku`, `plan_sku`, `org_entitlement`, `org_business_model`.
* **Metering Ingest**: idempotent event collector (`request_id`), durable queue, late arrival tolerant; supports replay.
* **Pricing Engine**: computes charges per event/rollup; supports tiered pricing; currency rounding; tax codes.
* **Ledger/Settlement**: writes `ledger` lines; applies PoR commission; runs real‑time payouts (threshold) and weekly sweeps; refunds reverse entries.
* **Estimator API**: deterministic preview using the same pricing rules as engine; no side effects; cached.

### 2.2 Contracts (selected)

* **POST /verify/email-submit** → `{ token, from_domain, dkim_pass, spf_pass, dmarc_aligned }` → `200 {status}`.
* **POST /metering/events** batch → `[{request_id, sku, quantity, org_id, project_id, time}]` → `202` on enqueue.
* **POST /pricing/estimate** → `{org_id, project_id, skus:{sku: uses_per_lead}, leads}` → `{ base, lines:[{sku, included, overage, total}], grand_total }`.
* **POST /billing/charges** → pricing → ledger lines (with PoR split).

### 2.3 Non‑functional Requirements

* **Idempotency**: `request_id` enforced at metering ingest; pricing safe to replay.
* **Consistency**: eventual consistency OK; nightly reconciliation against provider logs (SMS/email).
* **Scalability**: queue‑backed ingest; per‑org partitions; shard ledger tables by month.
* **Resilience**: provider abstractions; fallback queues; dead‑letter with replay.
* **Cost Guardrails**: budgets/caps enforced at engine and at action initiation (e.g., SMS send).
* **Security**: least privilege; signed webhooks; PII minimization in events; role‑based model assignment.

### 2.4 Risks & Mitigations (Architect)

* **Metering drift** ↔ nightly reconciliation + anomaly alerts.
* **Email spoofing** ↔ DMARC alignment & header capture hashed into `proof`.
* **Partner disputes** ↔ PoR rules + audit + dispute tooling.
* **Cost spikes** ↔ budgets, caps, prepaid credits for SMS/validations.

---

## 3) UX Design (UX Expert Deep Feedback)

### 3.1 Builder Estimator Panel

* **Placement**: right rail; sticky.
* **Elements**: model/plan badge; 100‑lead default; slider (10 → 10k); per‑SKU lines with included vs overage; total.
* **Copy**: “Costs scale with your results. Adjust objects/validations to tune cost.”
* **Warnings**: show prepaid requirement for SMS/validations; cap nearing banners at 80%.
* **Telemetry**: open panel, slider change, add/remove object, estimate shared/downloaded.
* **Accessibility**: keyboard for slider (step changes announced); ARIA roles on totals update.

### 3.2 Admin — Model Assignment (System Admin only)

* Model & Plan selectors; entitlement overview; override editor; audit badges; role‑gated.

### 3.3 Users & Invites / Domain Claims

* Tabs: Invites, Join Requests, Domain Claims. Clear instructions for email token send; verification states; wildcard guardrails.
* Privacy‑safe de‑dup hint with CTA to Join Request; never reveal member names.

### 3.4 Partner Directory (P2)

* Opt‑in profile editor; partner portal search; lead forms routed via platform; audit of outreach.

### 3.5 Error/Empty States & Copy

* DKIM/SPF/DMARC failed → “We couldn’t verify mail is from your domain. Try a different sender or contact IT.”
* Estimator when price missing → “Ask your admin to enable pricing for this object.”

---

## 4) Pricing Model Logic (Formulas & Examples)

### 4.1 Base + Consumption

* `total = base_pack_price + Σ over SKUs (max(0, uses - included_qty) * overage_price)`
* Example at 100 leads: Email verify (1/use/lead) at \$0.02, Address verify (1/use/lead) at \$0.05, 1 confirmation email at \$0.003 → variable \$8.3 + base.

### 4.2 Tiered Overage (optional)

* Tiers as JSON: `[{"threshold":1000,"price":0.018},{"threshold":5000,"price":0.015}]`.

### 4.3 Budgets/Caps

* Budget per org per month; alerts 50/80/100; hard cap pauses chargeable actions with override for Admins.

---

## 5) Backlog (v2) — Epics, Enablers, Features with ACs

### Epic: Foundations

* **ENA-DomainClaims-Email** — email challenge with DMARC; wildcards after root verify; conflict workflow; audit.
* **ENA-PoR-Ledger** — partner\_of\_record, commission\_rate, ledger; real‑time split ≥ threshold + weekly sweep; statements.
* **ENA-Entitlements** — product\_sku, plan\_sku, org\_entitlement, org\_business\_model; admin assignment UI; audit.
* **ENA-Metering-Service** — ingest, idempotency, queue, replay; provider adapters for SMS/email.

### Epic: Consumption UX & Billing

* **ST-Builder-Estimator** — panel UI; estimates at 100 leads; slider; warnings; telemetry; ACs for accuracy vs engine.
* **ST-Consumption-PricingEngine** — nightly & on‑demand pricing; ledger lines; refunds reverse; taxation hooks.
* **ST-Budgets-Caps-Alerts** — budgets; alerts; hard cap behavior; admin override.
* **ST-Validation-AddOns** — email/address/phone checks; prepaid credits; rate limits; error UX.
* **ST-Action-Services** — email/SMS/doc‑gen/webhook retries metered; quotas.
* **ST-P1-Private-Suggestions** — private de‑dup hints; Join Requests; audits.
* **ST-P2-Partner-Directory** — opt‑in directory; partner portal; lead forms.

(Each story includes detailed ACs mirroring earlier docs; use this as canonical.)

---

## 6) Migration Plan (Alembic Order)

1. `20250920_01_domain_claims_email.py`
2. `20250920_02_por_commission_ledger.py`
3. `20250920_03_business_model_entitlements.py`
4. `20250920_04_metering_events.py`
   (Seed SKUs/plans; backfill minimal defaults; non‑breaking toggles.)

---

---

## 9) Appendices

* **SKU Examples**: VAL-EMAIL (\$0.02), VAL-ADDR (\$0.05), ACT-EMAIL (\$0.003), ACT-SMS (\$0.04), OBJ-ADDRPICK (over-bundle \$0.002/lead).
* **Copy Strings**: privacy-safe hints; verification instructions; estimator warnings.
* **Test Matrix**: unit, integration, e2e per epic; staging smoke checklist.

# Head Office Dashboard — Wireframes & UX Spec (v2)

Multi‑org hierarchy + group billing dashboard for Head Office (parent org) with Assist Mode, budgets/caps, and consolidated billing.

> Scope: Web app (desktop‑first, responsive to tablet). Aligns with **Restart v2 Master Spec & Execution — Event Builder** (Sections 10.x).

---

## 1) Information Architecture

```
Head Office Dashboard
├─ Overview (Group KPIs + Subsidiary Grid + Org Tree)
├─ Billing
│  ├─ Consolidated Invoice (Billing Account)
│  └─ Ledger Explorer
├─ Subsidiary (Org Detail)
│  ├─ Overview
│  ├─ Projects & Forms
│  ├─ Budgets & Caps
│  ├─ Users & Invites
│  ├─ Domain Claims
│  └─ Entitlements & Plans
├─ Administration
│  ├─ Business Model & Plan Assignment
│  ├─ Group Roles & Access
│  └─ Alerts & Notifications
└─ Assist Mode (session banner + modal)
```

---

## 2) Wireframes (Lo‑Fi ASCII + Notes)

### 2.1 Overview (Group)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ [Logo] Head Office: Inchcape  [Org Switcher]    [Search ▢]  [Date: MTD]│
│ [Quick Actions: +Invite Subsidiary] [Start Assist] [Assign Model/Plan]  │
├─────────────────────────────────────────────────────────────────────────┤
│  Org Tree (left)             │   KPI Cards (right)                      │
│  ┌───────────────┐           │   ┌───────┐  ┌───────┐  ┌───────┐       │
│  │ ▸ Inchcape    │           │   │ Spend │  │ Leads │  │ Events│       │
│  │   ▾ Subaru AU │           │   └───────┘  └───────┘  └───────┘       │
│  │   ▾ PCA       │           │   ┌──────────────┐  ┌─────────────────┐ │
│  │   ▸ AutoNexus │           │   │ Budget Used  │  │ Domain Claims    │ │
│  └───────────────┘           │   └──────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ Subsidiary Grid (sortable, filterable)                                  │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Org          │ Model/Plan   │ Leads  │ Spend  │ Budget% │ Last Pub │ │
│ │ Subaru AU    │ Consump/Pro  │ 12,341 │ $7,204 │ 82%     │ 1d ago   │ │
│ │ PCA          │ Retail/Std   │ 5,103  │ $2,115 │ 47%     │ 3d ago   │ │
│ │ AutoNexus    │ Consump/Std  │ 2,224  │ $1,090 │ 33%     │ 14d ago  │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│ Row actions: [Assist] [Assign Plan] [Budget] [Open Billing] [More⋯]     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Notes**

* **Org Tree** uses ARIA `role="tree"` with keyboard expand/collapse; shows indicators (alerts, verification pending).
* **KPIs** reflect **selected date range** with tooltips for definitions.
* **Grid** supports bulk actions and CSV export.

### 2.2 Billing — Consolidated Invoice

```
┌───────────────────────────────────────────────────────────────┐
│ [Billing Account: Inchcape Group] [Period: Sep 2025] [Export] │
├───────────────────────────────────────────────────────────────┤
│   Summary: Spend ($), Partner Commissions ($), Net ($)        │
├───────────────────────────────────────────────────────────────┤
│ Ledger Rollup                                                  │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ Org        │ SKU        │ Qty   │ Gross   │ Partner │ Net │ │
│ │ Subaru AU  │ VAL-EMAIL  │ 12k   │ $240.00 │ $36.00  │$204 │ │
│ │ PCA        │ ACT-SMS    │ 6k    │ $240.00 │ $36.00  │$204 │ │
│ └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

**Notes**

* Filters by org, SKU, project; drill‑down to **Ledger Explorer**.
* Shows PoR precedence and commission splits.

### 2.3 Subsidiary — Org Detail

```
┌─────────────────────────────────────────────────────────────┐
│ Subaru AU  [Assist] [Assign Plan] [Budget] [Open Billing]   │
├─────────────────────────────────────────────────────────────┤
│ Tabs: Overview | Projects & Forms | Budgets & Caps | Users & Invites │
│       Domain Claims | Entitlements & Plans                        │
├─────────────────────────────────────────────────────────────┤
│ Overview KPIs + recent activity timeline                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 Assist Mode

```
┌───────────────────────────────────────────────────────────────┐
│ Start Assist Session                                          │
│ Purpose (required) [____________________________________]     │
│ Duration  [30 min ▼]  [Start Assist]                          │
└───────────────────────────────────────────────────────────────┘

[Banner in session]  You are assisting Subaru AU as Inchcape • Ends in 28:32 • [End]
```

### 2.5 Admin — Model & Plan Assignment

```
┌──────────────────────────────────────────────────────────────┐
│ Assign Business Model & Plan (System Admin Only)             │
├──────────────────────────────────────────────────────────────┤
│ Model  [Consumption ▼]   Plan [Pro ▼]   Effective [Now ▼]    │
│ Entitlements diff:  OBJ-ADDRPICK +100 included, VAL-EMAIL $0.02 → $0.018 │
│ [Preview 100 leads]  [Assign]                                 │
└──────────────────────────────────────────────────────────────┘
```

### 2.6 Budgets & Caps

```
┌──────────────────────────────────────────────────────────────┐
│ Group Budget (Sep 2025):  $25,000  [Edit]                     │
│ Subsidiary caps: Subaru AU $12,000 • PCA $8,000 • AutoNexus $5,000 │
│ Alerts at 50/80/100%                                          │
└──────────────────────────────────────────────────────────────┘
```

### 2.7 Domain Claims Across Group

```
┌──────────────────────────────────────────────────────────────┐
│ Domains                                                       │
│ acme.com  VERIFIED   • wildcard allowed                       │
│ subaru.com.au PENDING • verify via email                      │
│ autonexus.com  VERIFIED                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 3) Components & Design System Notes

* **Tree**: ARIA `tree`, `treeitem`, `group`; left/right to expand; home/end to jump.
* **Cards**: elevation sm, rounded‑xl; color tokens: `bg-card`, `text-muted-foreground`.
* **Tables**: sticky header; row hover actions; bulk select; async pagination.
* **Banners** (Assist): high‑contrast (amber), persistent across views.
* **Badges**: status (success, warning, danger) for budgets and domain claims.
* **Icons**: lucide-react (Building, TreeDeciduous, CreditCard, ShieldCheck, LifeBuoy).

---

## 4) Copy & States

**Privacy‑safe hints**: “We found a similar company. Request to join?”
**Assist banner**: “You are assisting {org} as {head\_office}. All actions are audited.”
**Empty**: “No subsidiaries yet—invite one to get started.”
**Errors**: “Verification failed (DMARC mismatch). Try a different sender.”

---

## 5) Accessibility

* Keyboard tree navigation; visible focus; aria‑live updates on KPI totals.
* Assist banner announced via `role="status"` on start/end.
* Slider controls (budgets/estimator) with `aria-valuenow`, `aria-valuetext`.

---

## 6) Telemetry & KPIs

* Events: `assist_start`, `assist_end`, `assign_plan`, `budget_update`, `domain_verify_attempt`, `domain_verify_success`, `estimator_open` (builder), `subsidiary_row_action`.
* Dashboard KPIs: group spend, commissions, net, leads, events, domain verification rate, budgets at risk.

---

## 7) Acceptance Criteria (Dashboard)

1. **Org Tree** reflects `org_hierarchy` and loads <300ms for 100 nodes (cached).
2. **KPIs** match ledger/metering aggregates for the selected period.
3. **Subsidiary Grid** sorts/filters; bulk actions apply to selected rows; exports CSV.
4. **Assist Mode** requires purpose; shows banner; all actions audited with actor + target.
5. **Consolidated Billing** shows PoR overrides and per‑org subtotals; exports invoice PDF & CSV.
6. **Budgets/Caps** editing updates limits immediately; caps enforced across child orgs.
7. **Domain Claims** table reflects statuses and provides verify actions; wildcard only post root verify + Owner + 2FA.

---

## 8) Dev Notes & API Mapping

* **Org Tree**: `GET /orgs/tree?root={id}`
* **KPIs**: `GET /metrics/group?account={billing_account_id}&range=…`
* **Grid**: `GET /orgs?parent={id}&q=…&sort=…`
* **Assist**: `POST /assist-sessions` with `{target_org_id, purpose, ttl}`
* **Billing**: `GET /billing-accounts/{id}/invoices?period=…`
* **Budgets**: `POST /budgets` and `GET /budgets?scope=account|org`
* **Domains**: `GET /domains?scope=group`, `POST /domains/{id}:verify`

---

## 9) Next Steps

* UX: translate wires to Figma; attach component specs and tokens.
* PM: confirm labels, column sets, and default ranges.
* Dev: build skeleton routes & feature flags; implement read models first.

---

## 11) Incorporation of “Head Office Dashboard — Wireframes & UX Spec (v2)”

This wireframe/UX spec is now part of the v2 baseline.

**Where it fits**

* **PRD v2**: Add a new section *Enterprise Multi‑Org & Group Billing UX* summarizing user goals, KPIs, actions, and compliance notes from the dashboard spec.
* **Architecture v2**: Ensure endpoints/read models listed in the dashboard spec (Org Tree, Metrics, Billing, Budgets, Domains, Assist) are reflected in API contracts and services.
* **Front‑End Spec v2**: Treat the dashboard spec as the canonical UI for parent‑org workflows; merge screens, copy, ARIA, telemetry, and ACs.

**Sharding target paths**

* `docs/prd/enterprise-multi-org-and-group-billing.md`
* `docs/architecture/group-billing-and-hierarchy-apis.md`
* `docs/front-end-spec/head-office-dashboard.md`

**Backlog linkage**

* Stories already defined in Section 10.9 (ENA‑OrgHierarchy, ENA‑GroupBilling, ST‑HeadOffice‑Dashboard, ST‑Assist‑Mode, ST‑Group‑Entitlements) must reference the UI acceptance criteria from the dashboard spec.


10) Multi‑Org Hierarchies & Group Billing (Parent ↔ Subsidiaries)
10.1 Objectives

Allow a Head Office org to onboard and manage subsidiary orgs with autonomy.

Enable consolidated billing (head office absorbs or allocates costs) while preserving sub‑org privacy and control.

Provide cross‑org visibility (KPIs, projects, budgets) and assist mode for setup with full audit.

10.2 Data Contracts (DDL)

organization (augment): add parent_org_id uuid null for simple hierarchy; soft constraint that if set, parent must exist.

org_hierarchy (closure table for fast queries): ancestor_org_id uuid, descendant_org_id uuid, depth int, PRIMARY KEY(ancestor_org_id, descendant_org_id).

billing_account: billing_account_id uuid pk, owner_org_id uuid fk, name, currency, status, notes.

org_billing_mapping: org_id uuid fk, billing_account_id uuid fk, allocation ENUM('absorb','chargeback','split'), percent numeric(5,2) null, effective_at timestamptz, PRIMARY KEY(org_id, billing_account_id, effective_at).

cost_center (optional): cost_center_id pk, billing_account_id fk, code, name.

project (augment): cost_center_id uuid null.

group_role_membership: ancestor_org_id, user_id, role ENUM('GroupAdmin','GroupBilling','GroupSupport'), PRIMARY KEY(ancestor_org_id, user_id).

Notes: keep membership (org‑scoped) for local roles; use group_role_membership for head‑office‑wide privileges across descendants.

10.3 Billing & Commissions

Consolidation locus = billing_account.

Invoicing pulls ledger lines for all org_id mapped to the billing_account during the period.

Allocation strategies:

absorb: 100% on head office invoice.

chargeback: individual sub‑org invoice copies emitted (for visibility) and head office master invoice (netting rules defined), or head office only with line‑level org_id tags.

split: percentage split between head office and sub‑org (rare; used for joint initiatives).

Partner‑of‑Record precedence: if a billing_account has a PoR, it overrides sub‑org PoRs for those lines; otherwise, fallback to each line’s org_id PoR.

10.4 Entitlements & Policies

Inheritance: a billing_account may define a default plan + SKU overrides that apply to all mapped orgs unless a child has explicit overrides.

Budgets & caps: can be set at billing_account (group budget) and/or per‑org; engine enforces the tighter constraint.

10.5 Domain Claims Across Group

Head office may verify corporate domains and delegate sub‑domains to subsidiaries (store delegation in proof with list of allowed sub‑orgs).

Sub‑orgs can still add unique domains; conflicts trigger the existing escalation workflow.

10.6 Security & Privacy

Assist Mode (Assume Role): GroupAdmin can open a scoped session within any descendant org; all actions are impersonation‑audited (actor, target org, purpose note).

Data boundaries: group views show aggregates and configuration, but PII access inside a sub‑org still obeys that org’s role permissions.

10.7 Services & APIs

Hierarchy Service: maintain org_hierarchy on create/move; supports read models for dashboards.

Billing Service: accepts billing_account and mapping changes; computes consolidated invoices; applies PoR precedence.

APIs (selected):

POST /orgs/{id}/children (create child or link existing)

POST /billing-accounts (create), POST /billing-accounts/{id}/map-org (mapping)

POST /groups/{ancestor_org_id}/roles (add GroupAdmin/Support/Billing)

POST /assist-sessions (start impersonation with purpose note); POST /assist-sessions/{id}:end

10.8 UX (Head Office Dashboard)

Org Tree & KPIs: cards for each child with events published, leads, spend, budgets %; drill‑down.

Quick Actions: “Invite subsidiary”, “Start assist session”, “Assign model/plan”, “Set budget/cap”, “Open billing account”.

Billing View: consolidated invoice lines grouped by org_id and cost_center; filters and export.

Audit Banner: visible when in Assist Mode.

10.9 Stories & ACs

ENA-OrgHierarchy: persistence + closure table; APIs; move org enforces cycle‑safety.

ACs: ancestor/descendant queries are O(1) via closure; moving a node updates paths; audited.

ENA-GroupBilling: billing_account + mapping; consolidated invoice generation; PoR precedence rules.

ACs: ledger aggregation across children; invoices show per‑org subtotals; PoR override verified in tests.

ST-HeadOffice-Dashboard: org tree, KPIs, drill‑downs; budgets overview; export.

ACs: totals = sum of child metrics; access requires GroupAdmin.

ST-Assist-Mode: impersonation with purpose note; banner; full audit trail; timed expiry.

ACs: all changes while impersonating carry actor/target metadata; logs immutable.

ST-Group-Entitlements: set default plan at billing_account; children inherit unless explicitly overridden; UI shows effective entitlements.

ACs: engine uses effective entitlements for pricing; child overrides win.

10.10 Migrations (extend order)

20250920_05_org_hierarchy_and_billing_accounts.py — adds hierarchy + billing account tables and mappings; backfill: make existing orgs root; create default billing_account per root.

10.11 Owner Runbook Additions

Create head office org; link subsidiaries via children endpoint or admin UI.

Create billing account at head office; map subsidiaries with absorb allocation.

Assign group plan and budgets; verify Assist Mode policy and audit retention.