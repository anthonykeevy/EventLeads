# ST-Budgets-Caps-Alerts

Type: Story
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-Metering-Service"]

## Description
Implement budgets and caps with alerts, enforcement at engine and at action adapters, and admin override.

## Acceptance Criteria
1. Budgets and caps configurable per org and at billing account; tighter constraint enforced.
2. Alerts at 50/80/100% thresholds; UI banners and notifications appear.
3. Action adapters block chargeable actions at hard cap with admin override.
4. Audit entries for budget edits and override actions.
