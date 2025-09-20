# PRD v2 Shard — Enterprise Multi‑Org & Group Billing UX

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/01-builder-ux.md`
Cross‑docs: `docs/front-end-spec/head-office-dashboard.md`, `docs/architecture/group-billing-and-hierarchy-apis.md`

## Scope
Enterprise parent orgs manage subsidiaries with consolidated billing, budgets/caps, Assist Mode, and domain claims across the group. This shard defines UX scope, behavior, and acceptance criteria, integrating with pricing, ledger, and domain verification.

## User Goals
- Monitor group KPIs and budgets; view PoR commissions.
- Assign business model/plan per subsidiary; preview entitlements deltas.
- Start Assist sessions with audit.
- Manage budgets/caps and domain claims across orgs.

## Key Behaviors
- Consolidated invoice view with per‑org and SKU rollups; PoR split visibility; export PDF/CSV.
- Org Tree with ARIA roles; performant and accessible.
- Budgets & caps with alerts at 50/80/100%; enforced across child orgs.
- Domain claims management with verify actions and wildcard guardrails.

## Acceptance Criteria (links)
- Mirrors `docs/front-end-spec/head-office-dashboard.md` ACs 1–7.
- Cross‑checks against API read models in `docs/architecture/group-billing-and-hierarchy-apis.md`.

## Out of Scope (P2)
- Public Partner Directory (opt‑in); partner portal search.

## Dependencies
- ADR‑005 (Hierarchy & Group Billing), ADR‑001 (PoR & Commissions), ADR‑002 (Domain Claims).
