# ST-Group-Entitlements

Type: Story
Status: Planned
Epic: Enterprise
Links.requires: ["ENA-Entitlements"]
ADR refs: `docs/adr/ADR-003-Entitlements-and-PricingLayers.md`, `docs/adr/ADR-005-Org-Hierarchy-and-Group-Billing.md`

## Description
Implement group entitlements where a billing account can define default plan and SKU overrides that child orgs inherit unless explicitly overridden; effective entitlements visible in UI.

## Acceptance Criteria
1. Billing account can set model/plan and SKU overrides; children inherit by default.
2. Effective entitlements computed per child; UI shows diffs vs group defaults and local overrides.
3. Pricing Engine uses effective entitlements for all pricing; tests cover inheritance precedence.
4. Audit entries on group defaults and child overrides.
