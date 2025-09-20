# Group Billing and Hierarchy APIs (v2)

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/01-builder-ux.md`
ADR refs: `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`

## Endpoints & Read Models (updates)
- Org Tree: `GET /orgs/tree?root={id}` → closure-backed; cached; <300ms for 100 nodes.
- Children mgmt: `POST /orgs/{id}/children` → create/link child; cycle-safe move updates closure.
- Billing Accounts: `POST /billing-accounts`, `POST /billing-accounts/{id}/map-org` (absorb/chargeback/split with percent), `GET /billing-accounts/{id}/invoices?period=…`.
- Group Roles: `POST /groups/{ancestor_org_id}/roles` to add `GroupAdmin|GroupBilling|GroupSupport`.
- Assist Sessions: `POST /assist-sessions` start with purpose; `POST /assist-sessions/{id}:end`.

## Data & Rules (additions)
- Allocation strategies:
  - absorb: 100% on head office invoice.
  - chargeback: emit individual sub‑org invoice copies for visibility and/or master invoice with org_id tags.
  - split: percentage split between head office and sub‑org.
- PoR precedence: billing_account PoR overrides child org PoRs; otherwise use per‑line org PoR.
- Cost centers: optional `cost_center` with `project.cost_center_id` to group ledger lines in consolidated views.

## Read Model Notes
- Precompute aggregates for selected period; reconcile vs ledger/metering.
- Show PoR precedence and commission splits in consolidated billing.
- Enforce privacy: do not leak member identities across orgs.

## Acceptance Criteria (links)
- Ledger aggregation across children; invoices show per‑org subtotals; PoR override verified.
- Cycle‑safety on org moves; closure table ancestor/descendant queries O(1).
- See `docs/front-end-spec/head-office-dashboard.md` for UX ACs.
