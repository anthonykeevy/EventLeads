# ST-Builder-Estimator

Type: Story
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-Entitlements", "ENA-Metering-Service"]

## Description
Implement Builder right‑rail estimator with 100‑lead default, slider, per‑SKU breakdown, budgets/caps warnings, and telemetry.

## Acceptance Criteria
1. Slider supports keyboard with ARIA; leads 10 → 10k; `aria-valuenow` and `aria-valuetext` set.
2. Per‑SKU lines reflect included vs overage; totals update via `aria-live`.
3. Warnings for missing price and budget nearing cap at 80%.
4. Telemetry emitted: `estimator_open`, `estimator_leads_change`, `estimator_sku_adjust`, `estimator_export`.
5. Estimates match Pricing Engine within tolerance across 10‑SKU matrix.
