# ST-HeadOffice-Dashboard

Type: Story
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-OrgHierarchy", "ENA-GroupBilling"]

## Description
Build Head Office Dashboard screens: Org Tree, KPI cards, Subsidiary Grid, Consolidated Billing, Subsidiary Detail, Assist Mode, Model & Plan Assignment, Budgets & Caps, Domain Claims across group.

## Acceptance Criteria
1. Org Tree <300ms for 100 nodes (cached) with ARIA tree roles and keyboard navigation.
2. KPIs match ledger/metering aggregates for selected period.
3. Subsidiary grid supports sort/filter, bulk actions, CSV export.
4. Assist Mode requires purpose; shows banner; all actions audited with actor + target; timed expiry.
5. Consolidated billing shows PoR overrides and per‑org subtotals; exports invoice PDF & CSV.
6. Budgets/Caps editing updates limits immediately; caps enforced across child orgs.
7. Domain Claims table reflects statuses and verify actions; wildcard only post root verify + Owner + 2FA.
8. Domain Delegation: Head Office can delegate sub‑domains to subsidiaries only after root domain verified; delegation list stored in claim proof; actions audited; UI copy: “Delegate sub‑domains to subsidiaries you control.”
