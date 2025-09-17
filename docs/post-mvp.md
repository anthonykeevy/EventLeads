# Post‑MVP Considerations

This document proposes high‑value epics after MVP. It groups opportunities, notes dependencies, and suggests acceptance gates to keep scope disciplined.

## Themes
- Growth & Adoption: analytics, CRM integrations, notifications
- Builder Pro: advanced layout tools, templates, collaboration
- Reliability & Compliance: SSO, audit, GDPR/PII, observability
- Globalization: multi‑language forms, locale formats, theming/branding
- Operability: admin tools, reconciliation, support workflows

## Candidate Epics

### E1. Conditional Logic & Advanced Fields
- Why: Higher conversion and flexibility for enterprise use cases
- Scope: conditional show/hide, computed fields, multi‑step forms, file upload, signature
- Depends: M3–M6 (form model & status/gating)
- Acceptance: logic editor with preview parity; server validation mirrors client; tests for 10+ scenarios

### E2. Analytics & Reporting
- Why: Customers need insight into event performance and lead quality
- Scope: event/form dashboards (submissions, conversion, device mix), exportable reports
- Depends: M9 leads
- Acceptance: drill‑down from event → form → time range; CSV/PNG exports

### E3. CRM & Marketing Integrations
- Why: Reduce manual exports; fit into customer stacks
- Scope: Salesforce/HubSpot first‑party, generic webhooks + Zapier
- Depends: M9, permissions
- Acceptance: reliable delivery with retries; per‑integration health; mapping UI

### E4. Collaboration & Review
- Why: Teams coordinate on complex form designs
- Scope: comments/mentions, review mode, share links, activity log
- Depends: M4–M6
- Acceptance: comment threads tied to objects; email notifications; permissions honored

### E5. Template Library & Theming
- Why: Faster starts, consistent branding
- Scope: starter templates, saved user templates, brand colors/logos, dark mode
- Depends: M4 builder
- Acceptance: apply template w/o breaking layout; theming tokens; preview parity

### E6. Multi‑Language Forms (i18n)
- Why: Global events
- Scope: translate labels/options, locale detection, right‑to‑left support
- Depends: M5 preview/public render
- Acceptance: language toggle in preview; language‑specific exports

### E7. SSO & Enterprise Security
- Why: Larger orgs require SSO and auditability
- Scope: SAML/OIDC SSO, SCIM (optional), audit log UI, encryption at rest for PII
- Depends: M1 auth
- Acceptance: IdP integration guide; audit queries/export; key rotation playbook

### E8. Offline Kiosk Mode v2
- Why: Improve reliability at venues
- Scope: background sync, conflict resolution, device lock, kiosk PIN
- Depends: MVP offline
- Acceptance: 100% successful sync after extended offline; admin device log

## Prioritization (suggested)
1) E1 Conditional Logic (customer pull, medium effort)
2) E3 CRM Integrations (speeds adoption)
3) E2 Analytics (retention & value)
4) E5 Templates/Theming (time‑to‑value)
5) E7 SSO/Enterprise (sales blocker removal)

## Guardrails
- Maintain preview=production render parity
- Keep builder at 60fps; performance budget per feature
- Backed migrations with feature flags and rollbacks

## Tracking
- Convert selected epics into roadmapped milestones (M13+)
- Each epic must include: rationale, dependencies, acceptance criteria, rollout plan
