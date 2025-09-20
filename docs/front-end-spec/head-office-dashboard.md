# Head Office Dashboard — Wireframes & UX Spec (v2)

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/01-builder-ux.md`
Cross‑docs: `docs/prd/v2-prd.md`, `docs/architecture/group-billing-and-hierarchy-apis.md`

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

## 2) Wireframes (ASCII + Notes)
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

### 2.2 Billing — Consolidated Invoice
```
┌───────────────────────────────────────────────────────────────┐
│ [Billing Account: Inchcape Group] [Period: Sep 2025] [Export] │
├───────────────────────────────────────────────────────────────┤
│   Summary: Spend ($), Partner Commissions ($), Net ($)        │
│   Allocation: absorb | chargeback | split (% shown)           │
├───────────────────────────────────────────────────────────────┤
│ Ledger Rollup                                                  │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ Org        │ Cost Ctr │ SKU        │ Qty   │ Gross │ PoR │ │
│ │ Subaru AU  │ MKT-001  │ VAL-EMAIL  │ 12k   │ $240  │$36  │ │
│ │ PCA        │ SALES    │ ACT-SMS    │ 6k    │ $240  │$36  │ │
│ └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

Notes
- Show PoR precedence: if billing account PoR exists, badge and explain override.
- Group by `org_id` and optional `cost_center`.

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

## 3) Components & Design System Notes
- Tree: ARIA `tree`, `treeitem`, `group`; left/right to expand; home/end to jump.
- Cards: elevation sm, rounded‑xl; color tokens: `bg-card`, `text-muted-foreground`.
- Tables: sticky header; row hover actions; bulk select; async pagination.
- Banners (Assist): high‑contrast (amber), persistent across views.
- Badges: status (success, warning, danger) for budgets and domain claims.
- Icons: lucide-react.

## 4) Copy & States
- Privacy‑safe hints: “We found a similar company. Request to join?”
- Assist banner: “You are assisting {org} as {head_office}. All actions are audited.”
- Empty: “No subsidiaries yet—invite one to get started.”
- Errors: “Verification failed (DMARC mismatch). Try a different sender.”

## 5) Accessibility
- Keyboard tree navigation; visible focus; aria‑live updates on KPI totals.
- Assist banner announced via `role="status"` on start/end.
- Slider controls (budgets/estimator) with `aria-valuenow`, `aria-valuetext`.

## 6) Telemetry & KPIs
- Events: `assist_start`, `assist_end`, `assign_plan`, `budget_update`, `domain_verify_attempt`, `domain_verify_success`, `estimator_open`, `subsidiary_row_action`.
- Dashboard KPIs: group spend, commissions, net, leads, events, domain verification rate, budgets at risk.

## 7) Acceptance Criteria
1. Org Tree reflects hierarchy; loads <300ms for 100 nodes (cached).
2. KPIs match ledger/metering aggregates for the selected period.
3. Subsidiary grid sorts/filters; bulk actions; exports CSV.
4. Assist Mode requires purpose; shows banner; all actions audited with actor + target.
5. Consolidated Billing shows PoR overrides and per‑org subtotals; exports invoice PDF & CSV.
6. Budgets/Caps editing updates limits immediately; caps enforced across child orgs.
7. Domain Claims table reflects statuses and provides verify actions; wildcard only post root verify + Owner + 2FA.
