# ENA-Entitlements

Type: Enabler
Status: Pending
Epic: Foundations
Links.requires: []
ADR refs: `docs/adr/ADR-003-Entitlements-and-PricingLayers.md`
Cross-docs: `docs/prd/v2-prd.md` (Entitlements & SKU Catalog), `docs/architecture/v2-architecture.md` (Catalog/Entitlements)

## Description
Implement product SKU catalog, plan SKU entitlements (included/overage/tiers), org entitlements, and business model assignment with audit and entitlement diff preview.

## Acceptance Criteria
1. SKU types: Hosting, Object, Validation, Action, Analytics; `product_sku` seeded.
2. `plan_sku` supports included, overage, and tier ladders; admin UI shows diffs.
3. `org_business_model` assignment persists with `effective_at`; overrides supported via `org_entitlement`.
4. Estimator uses same rules as Pricing Engine; deterministic and cached.
5. Audit entries on `plan_sku`, `org_entitlement`, and `org_business_model` writes.
