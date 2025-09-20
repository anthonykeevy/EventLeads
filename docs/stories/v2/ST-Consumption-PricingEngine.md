# ST-Consumption-PricingEngine

Type: Story
Status: Planned
Epic: Consumption UX & Billing
Links.requires: ["ENA-Entitlements", "ENA-Metering-Service"]
ADR refs: `docs/adr/ADR-003-Entitlements-and-PricingLayers.md`, `docs/adr/ADR-004-Consumption-Metering-and-Pricing.md`

## Description
Implement consumption pricing engine that computes charges from metering events, supports tiered pricing, currency rounding, and tax codes, and writes ledger lines. Provide parity with Estimator and nightly/on-demand pricing.

## Acceptance Criteria
1. Engine computes charges per event and rollup; supports tier ladders from `plan_sku.tiers`.
2. Currency rounding rules and tax codes applied; results deterministic and replay-safe.
3. Nightly batch pricing and on-demand pricing endpoints produce identical results for the same inputs.
4. Parity with Estimator validated via golden 10‑SKU matrix; deviations flagged.
5. Idempotency: repeated pricing requests with same `request_id` do not duplicate ledger lines.
