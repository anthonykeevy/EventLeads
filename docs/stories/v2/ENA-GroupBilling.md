# ENA-GroupBilling

Type: Enabler
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-OrgHierarchy", "ENA-PoR-Ledger"]
ADR refs: `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`
Cross-docs: `docs/prd/v2-prd.md` (Enterprise UX), `docs/architecture/group-billing-and-hierarchy-apis.md`

## Description
Implement billing accounts, org mappings, allocation strategies (absorb/chargeback/split), consolidated invoices, and PoR precedence.

## Acceptance Criteria
1. Consolidated invoices pull ledger lines for mapped orgs within period; per‑org subtotals shown.
2. Allocation strategies applied; split supports percent.
3. Billing account PoR overrides child org PoRs; badge displayed in UI; tests verify precedence.
