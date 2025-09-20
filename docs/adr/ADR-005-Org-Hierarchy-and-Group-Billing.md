# ADR-005: Org Hierarchy and Group Billing (Head Office Dashboard)

Status: Accepted
Date: 2025-09-20

## Context
Enterprise customers require multi-org hierarchies, consolidated billing, Assist Mode, budgets/caps at group level, and domain claims visibility, presented via Head Office Dashboard.

## Decision
- Provide group-level read models and APIs:
  - Org Tree (`GET /orgs/tree?root={id}`) with ARIA-compliant UI.
  - Group KPIs and consolidated billing views (`GET /metrics/group`, `GET /billing-accounts/{id}/invoices`).
  - Assist Sessions (`POST /assist-sessions` with `{target_org_id, purpose, ttl}`) with audit.
  - Budgets APIs (`POST /budgets`, `GET /budgets?scope=account|org`).
  - Domains overview (`GET /domains?scope=group`).
- Ledger supports PoR split display and partner statements.
- Accessibility, telemetry, and acceptance criteria match dashboard spec.

## Consequences
- Requires hierarchy data model (next pass) and billing account aggregation.
- Assist Mode requires banner and session scoping across views with audit of actions.

## References
- PRD v2: Enterprise Multi-Org & Group Billing UX
- Architecture v2: Group billing endpoints/read models

Shard refs: `docs/shards/01-builder-ux.md`, `docs/shards/02-data-schema.md`

## Additions (2025-09-20)
- Data contracts:
  - `organization.parent_org_id` (nullable), closure table `org_hierarchy`.
  - `billing_account`, `org_billing_mapping(allocation: absorb|chargeback|split, percent)`.
  - Optional `cost_center` with `project.cost_center_id`.
  - `group_role_membership` for GroupAdmin/Billing/Support.
- Rules:
  - Consolidation locus is `billing_account`.
  - PoR precedence: billing account PoR overrides child org PoRs; else use per‑line org PoR.
  - Entitlements inheritance from billing account defaults to children unless overridden.
  - Group domain delegation: head office may verify corporate domains and delegate sub‑domains to subsidiaries (delegation list in claim `proof`).
- Migrations: `20250920_05_org_hierarchy_and_billing_accounts.py` adds hierarchy + billing accounts.

