# ADR-003: Entitlements and Pricing Layers (SKU Catalog + Plans)

Status: Accepted
Date: 2025-09-20

## Context
We require a normalized catalog of meterable capabilities across Hosting, Object, Validation, Action, and Analytics, with plan-level included quantities, overage pricing, and optional tiered rates. Per-org overrides must be supported.

## Decision
- Data contracts:
  - `business_model(model_id, code unique, name, status, version, currency, default_plan_id)`
  - `plan(plan_id, model_id fk, name, tier, status, notes)`
  - `product_sku(sku pk, type ENUM('hosting','object','validation','action','analytics'), unit, cost, retail, tax_code, metadata jsonb)`
  - `plan_sku(plan_id fk, sku fk, included_qty numeric, overage_price numeric, tiers jsonb, PRIMARY KEY(plan_id, sku))`
  - `org_entitlement(org_id fk, plan_id fk, overrides jsonb, effective_at, PRIMARY KEY(org_id, plan_id))`
  - `org_business_model(org_id fk, model_id fk, plan_id fk, assigned_by, assigned_at, notes)`
- Pricing logic: `total = base_pack_price + Σ max(0, uses - included_qty) * overage_price` with optional tiers.
- Estimator uses same rules as Pricing Engine; deterministic previews with cache.

## Consequences
- Requires catalog and plan management UI with audit.
- Estimator accuracy must be within defined tolerance of engine; shared rules library preferred.
- Enables per-org overrides and plan migrations with effective dates.

## References
- PRD v2: Entitlements & SKU Catalog; Consumption Billing & Estimator
- Architecture v2: Catalog/Entitlements Service; Pricing Engine

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/03-billing-go-live.md`

## Risks
- Misconfigured tiers or overrides can cause revenue leakage; require change review and audit.
- Plan migrations can create entitlement gaps; use effective_at and preview diffs before apply.

## Rollback Strategy
- Revert plan changes by restoring previous plan_id and overrides effective at next window; maintain audit.
- Disable tiered pricing via feature flag and fall back to flat overage_price.

