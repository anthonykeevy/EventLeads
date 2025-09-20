# ST-Assist-Mode

Type: Story
Status: Planned
Epic: Enterprise
Links.requires: ["ENA-OrgHierarchy"]
ADR refs: `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`

## Description
Implement Assist Mode allowing GroupAdmin to assist a subsidiary with scoped session, purpose requirement, visible banner, and full audit of actions with actor + target, with timed expiry.

## Acceptance Criteria
1. Start Assist requires purpose and ttl; creates session scoped to target org; access gated by GroupAdmin role.
2. Banner visible across views with timer; announced via `role="status"`.
3. All actions during assist carry actor and target org metadata; audit entries immutable.
4. Ending Assist clears session; expiry auto-ends; telemetry `assist_start` and `assist_end` emitted.
