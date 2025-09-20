# Sprint 1 Plan — Stories 0003–0006

Dates: Mon 2025-09-22 → Fri 2025-10-03 (2 weeks)
Goal: Establish onboarding, invites, dashboard scaffold, and Event CRUD so the team can start building Forms and the Visual Builder in Sprint 2.

Scope (Committed)
- 0003 Global Settings & Invitations (48h TTL)
- 0004 Organization Onboarding Wizard
- 0005 Dashboard Scaffold
- 0006 Events CRUD (Org-Scoped)

Proposed Owners
- Backend (primary): Story 0003, 0006; API support for 0004, 0005
- Frontend (primary): Story 0004, 0005; UI for 0003 (accept) and 0006 (list/create)
- DevOps (support): Secrets/env for SMTP/DB; migration checks; CI
- Product/QA: Story acceptance; demo content

Ceremonies & Key Dates
- 2025-09-22 Mon: Sprint Planning + Kickoff
- 2025-09-26 Fri: Mid-sprint review (UI demos: onboarding wizard, dashboard zero-state)
- 2025-10-02 Thu: Code freeze (feature complete); migration verification on SQL Server
- 2025-10-03 Fri: Sprint Review + Demo + Retro

Acceptance Gates
- Definition of Ready: stories linked; shard citations identified; test approach noted.
- Definition of Done:
  - Alembic migration(s) with downgrade; tested on SQLite (CI) and SQL Server (local/docker)
  - RBAC/org isolation enforced; structured logs with request_id
  - UI flows implemented (wizard, dashboard zero-state, event create/list)
  - Docs updated (story pages, roadmap); PR template checklist satisfied

Story Breakdown & Ownership
- 0003 Global Settings & Invitations
  - Backend (owner): GlobalSetting table + service; Invitation model + endpoints; rate limits; audit
  - DevOps: SMTP/MailHog; env keys; secrets handling
  - Frontend: Invite accept page (token → set password)
- 0004 Organization Onboarding Wizard
  - Frontend (owner): wizard UI + routing; validation; happy/error states
  - Backend: org create API; role assignment (creator=Admin); last-Admin protection
- 0005 Dashboard Scaffold
  - Frontend (owner): zero-state and populated lists; protected routes; basic queries
  - Backend: list endpoints with org scoping and indexes
- 0006 Events CRUD (Org-Scoped)
  - Backend (owner): endpoints; validations; soft-delete/restore (Admin-only); indexes
  - Frontend: event create/list UI; integrate with dashboard

Key Risks & Mitigations
- Env config (SMTP, DB): provide `.env.dev` defaults; verify MailHog early (Day 1–2)
- SQL Server compatibility: run local container check once migration is ready (by Day 8)
- Invite emails: log token link in dev; ensure rate limits don’t block testing

Shard Citations
- docs/shards/02-data-schema.md (tables, BIT booleans, indexes)
- docs/shards/04-auth-rbac.md (routing & enforcement examples)
- docs/shards/05-devops-migrations.md (alembic flow)

Deliverables
- Working onboarding and dashboard
- Events CRUD API + minimal UI
- Invitations issue/accept with 48h expiry (GlobalSetting)
