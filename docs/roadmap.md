# Product Roadmap (MVP) — Event Leads

This roadmap sequences MVP milestones with dependencies, entry/exit criteria, and example stories. Used by SM for planning and tracking.

Sprint 1: Stories 0003–0006
Sprint 2: Stories 0007–0013

## M0 — Auth & Org Foundation (Done)
- Outcome: JWT auth, email verification, RBAC; AppShell/routing.
- Depends: —
- Exit: Signup/verify/login/reset work; roles in JWT; protected routes.
- Stories: 0001 (done)

## M1 — Onboarding, Global Settings, Invitations
- Outcome: First-run org setup; global config (invite TTL); secure invites.
- Depends: M0
- Exit: Org wizard; GlobalSetting seeded (invite_token_ttl_hours=48); invite accept.
- Stories: 0003, 0004

## M1.5 — Dashboard Scaffold
- Outcome: Guided hub with zero/populated states.
- Depends: M1
- Exit: Empty prompts (create org, invite, create event); lists recent events/forms.
- Stories: 0005

## M2 — Events & Forms (Draft) + CanvasLayout + Field Types
- Outcome: Event CRUD; multiple draft Forms; initial CanvasLayout; FieldType registry.
- Depends: M1.5
- Exit: Org-scoped Event CRUD; Form CRUD (no slug); Desktop layout v1; seeds in place.
- Stories: 0006, 0007, 0008, 0009

## M3 — Visual Builder MVP (Hero Feature)
- Outcome: Desktop builder with snapping, properties, background image; previews.
- Depends: M2
- Exit: Place/edit objects; persist properties; preview with device fallback.
- Stories: 0010, 0011 (Text), 0012 (Dropdown), 0013 (Checkbox)

## M4 — Slug & Public Runtime
- Outcome: Slug issued on Ready/Publish; public render + submit (thin).
- Depends: M3
- Exit: Stable global slug; public page by slug; submission with validation and is_test.
- Stories: 0014

## M5 — Publish & Stripe Billing (MVP)
- Outcome: Admin publish; event-day guard; first-of-day UsageCharge; Stripe webhooks; invoice rollup.
- Depends: M4
- Exit: Publish path enforced; charges recorded; invoices reflect webhook outcomes.
- Stories: 0015

## M6 — Leads & Admin CSV Export
- Outcome: Leads list/detail, filters; CSV export (Admin only).
- Depends: M4–M5
- Exit: Filter test vs production; CSV admin-only enforced.
- Stories: (future)

## M7 — Observability & Admin
- Outcome: Metrics, tracing, health checks; audit queries.
- Depends: M0–M5
- Exit: /metrics, /healthz, /readyz live; admin audit queries functional.
- Stories: (future)

---

## Acceptance Gates (per milestone)
- Entry: previous milestone exit met; migrations applied; CI green.
- Exit: functional demo; tests for core logic; docs updated (spec, API, migrations).

## Cross‑Cutting
- Performance: 60fps builder interactions; sub‑100ms property updates.
- Accessibility: WCAG 2.1 AA for UI components; keyboard coverage.
- Observability: request IDs, structured logs; health endpoints.

---

## Post‑MVP Candidates
- Conditional Logic & Advanced Fields
- CRM Integrations
- Analytics & Reporting
- Template Library & Theming
- Multi‑Language Forms
- Collaboration & Review
- SSO & Enterprise Security
- Offline Kiosk Mode v2
