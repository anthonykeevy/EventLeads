# Product Roadmap (MVP) — Event Leads

This roadmap sequences MVP milestones with dependencies, entry/exit criteria, and example stories. Used by SM for planning and tracking.

## M1 — Auth & Org Foundation
- Outcome: JWT auth, email verification, invites; AppShell/routing.
- Depends: —
- Entry: Repos initialized; env set; CI green.
- Exit: Signup/verify/login/logout work; invite accept flow; basic roles in JWT.
- Stories: implement signup + verify; login/logout; invite create/accept; AppShell + protected routes.

## M2 — Event Management
- Outcome: Event CRUD with timezone + date range; dashboard zero-state.
- Depends: M1
- Exit: Create/edit/view events; timezone stored; zero-state CTA on dashboard.
- Stories: event list/detail; create/edit with validations; zero-state UI.

## M3 — Form & Canvas Model
- Outcome: Form entity; CanvasLayout/Object; ObjectType seeds.
- Depends: M2
- Exit: CRUD for Form/Layout/Object via API; seeds present; soft-deletes modeled.
- Stories: create form under event; seed object types; list/add canvas objects.

## M4 — Builder v1
- Outcome: Canvas, palette, properties, grid/snap, save draft.
- Depends: M3
- Exit: Place/move/resize objects; save/load draft reliably; 60fps target interactions.
- Stories: grid/snap; properties panel; undo/redo basic; save draft.

## M5 — Preview & Test Mode (+ Try-the-Builder)
- Outcome: Preview uses prod render path; flag test submissions; public demo (no save).
- Depends: M3–M4
- Exit: Test leads flagged; demo accessible from landing; save actions gated to auth.
- Stories: preview render; is_test flag; demo route and gating.

## M6 — Status Gating & Public Link
- Outcome: Draft → ReadyForReview → ProductionEnabled; production link slug.
- Depends: M5
- Exit: Cannot enable production until successful test submission; public link issued.
- Stories: status transitions; gate on test submission; slug generation.

## M7 — Event‑Day Guard & Usage Charges
- Outcome: Enforce date window by event timezone; record first‑of‑day usage.
- Depends: M2, M6
- Exit: Submissions blocked outside window; unique daily usage rows written.
- Stories: tz window calc + tests; usage insert with uniqueness.

## M8 — Stripe Integration & Webhooks
- Outcome: Checkout/charges; invoices from usage; webhooks idempotent.
- Depends: M7
- Exit: Payment success/failure reflected in invoices; recon note documented.
- Stories: checkout endpoint; webhook handler; invoice aggregation; recon job.

## M9 — Leads & Admin CSV Export
- Outcome: Leads list/detail, filters; CSV export (Admin only).
- Depends: M5–M6
- Exit: Filter test vs production; CSV admin-only enforced.
- Stories: leads table + filters; CSV export; permission gate.

## M10 — RBAC Enforcement
- Outcome: Permissions applied to all routes and UI.
- Depends: M1–M9
- Exit: Matrix-compliant behavior; audit logging for critical actions.
- Stories: route guards; UI hiding/disable; audit log writes.

## M11 — Onboarding Wizard
- Outcome: Dismissible first‑login guidance.
- Depends: M2–M6
- Exit: Wizard shown until dismissed; relaunch from Help.
- Stories: wizard steps; dismissal persistence.

## M12 — Soft Deletes & Restore UI
- Outcome: Admin archive/delete/restore flows.
- Depends: M2–M3
- Exit: Archive/delete/restore visible; audit trail; restore works.
- Stories: archive/delete actions; restore list; audit entries.

---

## Acceptance Gates (per milestone)
- Entry: previous milestone exit met; migrations applied; CI green.
- Exit: functional demo; tests for core logic; docs updated (spec, API, migrations).

## Cross‑Cutting
- Performance: 60fps builder interactions; sub‑100ms property updates.
- Accessibility: WCAG 2.1 AA for UI components; keyboard coverage.
- Observability: request IDs, structured logs; health endpoints.

---

## Post‑MVP Candidates (M13+)

- M13 — Conditional Logic & Advanced Fields (E1)
  - Outcome: logic editor, multi‑step forms, uploads/signature
  - Depends: M3–M6
  - Exit: preview parity; server validation; tests for key flows

- M14 — CRM Integrations (E3)
  - Outcome: Salesforce/HubSpot integrations; generic webhooks/Zapier
  - Depends: M9
  - Exit: reliable delivery with retries; integration health

- M15 — Analytics & Reporting (E2)
  - Outcome: dashboards, funnels, exportable reports
  - Depends: M9
  - Exit: drill‑down + time range; CSV/PNG exports

- M16 — Template Library & Theming (E5)
  - Outcome: starter templates, saved templates, theming tokens
  - Depends: M4
  - Exit: apply template safely; tokens documented

- M17 — Multi‑Language Forms (E6)
  - Outcome: multi‑language rendering and exports
  - Depends: M5
  - Exit: per‑language content with toggle

- M18 — Collaboration & Review (E4)
  - Outcome: comments/mentions; activity log; share links
  - Depends: M4–M6
  - Exit: comment threads; email notifications; permissions enforced

- M19 — SSO & Enterprise Security (E7)
  - Outcome: SAML/OIDC SSO; audit log UI
  - Depends: M1
  - Exit: IdP guide; audit queries/export; key rotation plan

- M20 — Offline Kiosk Mode v2 (E8)
  - Outcome: background sync + conflict resolution; device lock
  - Depends: MVP offline
  - Exit: reliable sync after extended offline; device logs
