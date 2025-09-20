# Scrum Master Brief — Sprint 1 Kickoff (September 2025)

Purpose: Share the updated plan, scope for Sprint 1, and key references.

## Summary
- We completed a Correct Course to move the Visual Builder earlier in MVP and defer slug/public runtime until after builder output.
- Stripe is included in MVP (publish, usage charges, webhooks).
- Stories have been resliced with shard citations and sprint groupings.

## Sprint Plan
- Sprint 1 (2025‑09‑22 → 2025‑10‑03): Stories 0003–0006
  - 0003 Global Settings & Invitations (48h TTL)
  - 0004 Organization Onboarding Wizard
  - 0005 Dashboard Scaffold
  - 0006 Events CRUD (Org-Scoped)
- Sprint 2 (next): Stories 0007–0013 (Forms draft, CanvasLayout, FieldType registry, Builder MVP + Text/Dropdown/Checkbox)

## Key Links
- Roadmap (tagged with sprints): docs/roadmap.md
- Sprint 1 Plan: docs/sprint-0001-plan.md
- Correct Course Note: docs/correct-course-2025-09.md
- PRD (MVP sequencing note added): docs/event-form-prd.md
- Technical Architecture (slug timing + Stripe-in-MVP + tables): docs/tech-architecture.md

## Process & Standards
- PRs must include shard citations and Alembic migration with downgrade
  - Template: .github/pull_request_template.md
- Shard Citations (developer references)
  - docs/shards/02-data-schema.md (tables, BIT booleans, indexes)
  - docs/shards/04-auth-rbac.md (RBAC & org isolation)
  - docs/shards/05-devops-migrations.md (alembic flow & rollback)
  - docs/shards/03-billing-go-live.md (Stripe usage charges & invoices)

## Risks & Requests
- Env/Secrets readiness: SMTP (MailHog dev), DB, Stripe keys & webhook secret
- SQL Server migration verification planned before sprint end
- Capacity/owners in Sprint 1 plan are proposed; please validate against team availability

## Ask
- Review and ratify Sprint 1 scope, owners, and dates
- Confirm ceremonies and any capacity adjustments
- Approve PR template usage for shard citations and migration checks

---

## Sprint 1 Task Breakdown (Junior‑friendly)

Story 0003 — Global Settings & Invitations (Backend primary)
- Migration 1: Create `GlobalSetting(id, key, value, value_type, scope, created_at, updated_at)`; seed `invite_token_ttl_hours=48` [shards: 02, 05] [Agents: dev (impl), architect (review)]
- Service: Implement settings loader with in‑process cache + TTL invalidation [shards: 02] [Agent: dev]
- Migration 2: Create `Invitation(id, org_id, email, role, token, expires_at, consumed_at, created_by, created_at)` + indexes on `(org_id, created_at)` and `(email)` [shards: 02, 05] [Agents: dev (impl), architect (review)]
- API A: POST `/api/v1/invitations` (Admin) → create invite; generate random token (≥32 bytes); set `expires_at` = now + TTL from GlobalSetting; return 201 without token in body [shards: 04] [Agent: dev]
- Rate limit: basic in‑memory throttle (e.g., 10/day/org) and `Retry-After` header on limit [shards: 04] [Agent: dev]
- Email (dev): log invite URL to console/MailHog; never print token in server logs [shards: 04] [Agent: dev]
- API B: POST `/api/v1/invitations/{token}/accept` → validate token (exists, unconsumed, unexpired); set password; add user to org with role; consume token; write audit [shards: 04] [Agent: dev]
- Tests: unit tests for expiry, single‑use, rate limit; downgrade path runs cleanly [shards: 05] [Agent: dev]
- Docs: update `docs/stories/0003-global-settings-and-invitations.md` status to In Progress → Done [Agent: pm]

Acceptance checks (0003)
- Settings seed present; Invitation rows create; accept flow joins org and consumes token; rate limit enforced; migrations downgrade successfully.

Dependencies
- Requires working email dev setup (MailHog) and auth from Story 0001.

---

Story 0004 — Organization Onboarding Wizard (Frontend primary)
- API A (BE): POST `/api/v1/orgs` with `{ name, billing_email, billing_address, timezone }`; creator becomes Admin; enforce ≥1 Admin invariant [shards: 02, 04] [Agent: dev]
- UI A (FE): Add route `/onboarding`; Step 1 form (Org info); client validation; error display [shards: 04] [Agent: dev]
- UI B: On success, redirect to `/dashboard`; show org card and next steps (Invite teammates, Create Event) [shards: 04] [Agents: dev, ux-expert]
- Guard: If user already has org, skip wizard and go to `/dashboard` [shards: 04] [Agent: dev]
- Tests: FE component tests (valid/invalid), BE tests for invariant (can’t remove last Admin) [shards: 04, 05] [Agent: dev]
- Docs: update `docs/stories/0004-organization-onboarding-wizard.md` status [Agent: pm]

Acceptance checks (0004)
- First‑login without org shows wizard; creates org; sets Admin; redirects to dashboard. Existing org skips wizard.

Dependencies
- Uses auth context and dashboard route (0005) for redirect.

---

Story 0005 — Dashboard Scaffold (Frontend primary)
- Route: Create `/dashboard` protected route using existing `AuthGate` [shards: 04] [Agent: dev]
- Empty state: If no org → CTA to Onboarding; if org no events → CTA to Create Event; CTA to Invite teammates [shards: 04] [Agents: dev, ux-expert]
- List: Implement events fetch → list recent events (paged, created_at desc); compute per‑event form counts (placeholder 0 for now) [shards: 02] [Agent: dev]
- Perf: Confirm DB indexes for events by org/date; add migration if missing [shards: 02, 05] [Agents: dev, architect]
- Tests: render empty vs populated; auth protection; error boundary [Agent: dev]
- Docs: update `docs/stories/0005-dashboard-scaffold.md` status [Agent: pm]

Acceptance checks (0005)
- Authenticated users see dashboard; correct empty prompts; events list appears when available; performance acceptable on sample data.

Dependencies
- Requires 0004 for org creation and 0006 for events listing.

---

Story 0006 — Events CRUD (Backend primary)
- Migration: Ensure `Event(id, org_id, name, timezone, start_date, end_date, status, is_deleted BIT, deleted_at, deleted_by)` + indexes `(org_id, created_at)` and `(org_id, start_date)` [shards: 02, 05] [Agents: dev, architect]
- API A: POST `/api/v1/events` with validation (timezone exists; end_date ≥ start_date) → 201 Draft [shards: 04] [Agent: dev]
- API B: GET `/api/v1/events` (org‑scoped, created_at desc), GET `/api/v1/events/{id}` (org‑scoped) [shards: 04] [Agent: dev]
- API C: PUT `/api/v1/events/{id}` (org‑scoped update) [shards: 04] [Agent: dev]
- API D: DELETE `/api/v1/events/{id}` (soft delete, Admin‑only), POST `/api/v1/events/{id}/restore` (Admin‑only) [shards: 04] [Agent: dev]
- FE wiring: Add simple create form + list integration on `/dashboard` [shards: 04] [Agent: dev]
- Tests: Validation, org isolation, Admin‑only delete/restore; migration downgrade verified [shards: 04, 05] [Agent: dev]
- Docs: update `docs/stories/0006-events-crud.md` status [Agent: pm]

Acceptance checks (0006)
- Create/list/get/update/delete/restore all work and are org‑scoped; RBAC enforced; indexes present; downgrade clean.

Dependencies
- Uses 0004 (org) and 0005 (dashboard wiring).

---

Notes for all tasks
- Always include shard citations in PR description
- Include downgrade in migrations and verify on SQLite (CI) and SQL Server (local/docker)
- Use structured logging with `request_id`; avoid leaking secrets in logs
