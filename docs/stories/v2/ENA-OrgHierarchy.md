# ENA-OrgHierarchy

Type: Enabler
Status: Pending
Epic: Foundations
Links.requires: []
ADR refs: `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`
Cross-docs: `docs/prd/v2-prd.md` (Enterprise UX), `docs/architecture/group-billing-and-hierarchy-apis.md`

## Description
Implement parent/child org hierarchy with closure table and group roles; cycle-safe moves; read models for dashboards.

## Acceptance Criteria
1. `org_hierarchy` closure maintained on create/move; ancestor/descendant queries O(1).
2. Move org updates closure paths; cycle safety enforced.
3. Group roles (GroupAdmin/Billing/Support) scoped across descendants; access audited.
