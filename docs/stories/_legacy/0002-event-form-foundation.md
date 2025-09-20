> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0002 — Event & Form Foundation (M1)

Status: Draft
Epic: M1 — Event & Form foundation
Owners: Backend, Frontend, DevOps
Related: docs/event-form-prd.md, docs/tech-architecture.md

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/02-data-schema.md#migration-notes-v0.2
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Establish the core domain objects and APIs for Events, Forms, and Canvas Layouts to unlock the visual builder and billing. This story implements the foundational database schema, basic CRUD endpoints, and minimal frontend scaffolding for listing/creating events and forms within an organization.

## User Stories
- As an authenticated user, I can create an Event with a name, timezone, start/end date.
- As an authenticated user, I can create a Form attached to an Event and see its public slug.
- As an authenticated user, I can view my organization’s Events and their Forms.
- As an Admin, I can soft-delete and restore Events and Forms.

## In Scope (MVP)
- Database tables per data schema shard for: `Event`, `Form`, `CanvasLayout`
- Soft delete fields on those tables per standards (is_deleted, deleted_at, deleted_by)
- Basic CRUD APIs scoped to organization via JWT claims (org_id)
- Public slug generation for Form (unique, stable)
- Indexes and constraints per shard
- Minimal frontend pages to list/create Events and Forms

Out of Scope
- Visual builder UX (separate story)
- Lead submission and CSV export (later stories)
- Billing and publish flows (separate story)

## Acceptance Criteria
1) Create Event
- POST /api/v1/events with {name, timezone, start_date, end_date}
- Then returns 201 with Event including id, org_id, status=Draft, soft-delete fields defaulted

2) List Events (Org scoped)
- GET /api/v1/events → returns only the caller’s org events ordered by created_at desc

3) Create Form for Event
- POST /api/v1/events/{id}/forms with {name}
- Then returns 201 with Form containing id, event_id, status=Draft, public_slug (unique), soft-delete fields

4) List Forms for Event
- GET /api/v1/events/{id}/forms → returns only forms for that event and org

5) CanvasLayout bootstrap
- POST /api/v1/forms/{id}/layouts with {device_type, aspect_ratio, resolution_x, resolution_y}
- Then returns 201 with revision_number=1

6) Soft delete/restore
- DELETE /api/v1/events/{id} marks is_deleted=1 with deleted_at/by
- DELETE /api/v1/forms/{id} marks is_deleted=1 with deleted_at/by
- POST /api/v1/events/{id}/restore and /api/v1/forms/{id}/restore revert deletion (Admin only)

7) Constraints & Uniqueness
- Form.public_slug is globally unique
- Field.key uniqueness per layout will be enforced in a later story; out of scope here

8) RBAC & Org Isolation
- All endpoints require auth and enforce org_id isolation
- Admin-only for delete/restore per shard 04-auth-rbac

## Data & Config
- Follow `docs/shards/02-data-schema.md` types and constraints
- Use BIT for booleans; SQLAlchemy Boolean mapped appropriately
- Enforce timezone stored on Event; start/end date present
- Add helpful indexes for frequent queries (events by org, forms by event)

## API (initial)
- POST /api/v1/events
- GET  /api/v1/events
- GET  /api/v1/events/{id}
- PUT  /api/v1/events/{id}
- DELETE /api/v1/events/{id}
- POST /api/v1/events/{id}/restore (Admin)
- POST /api/v1/events/{id}/forms
- GET  /api/v1/events/{id}/forms
- GET  /api/v1/forms/{id}
- PUT  /api/v1/forms/{id}
- DELETE /api/v1/forms/{id}
- POST /api/v1/forms/{id}/restore (Admin)
- POST /api/v1/forms/{id}/layouts

## Tasks (Dev)
Backend
- Add/confirm models: Event, Form, CanvasLayout with soft-delete fields
- Create Alembic migration (new revision) with upgrade/downgrade per shard 05
- Implement repositories/services with org scoping
- Implement routers for events, forms, layouts with RBAC per shard 04
- Add slug generator for Form with collision retries
- Add indexes/constraints per shard 02

Frontend (Next.js)
- Add basic Events list/create page
- Add Forms list/create under an Event detail page
- Wire to API; enforce protected routes

DevOps
- Run migration locally and in CI (SQLite) per shard 05
- Document env/config expectations

## QA Scenarios
- Create → list Events happy path
- Create → list Forms under event happy path
- Soft delete and restore flows (Admin only)
- Org isolation verified across users in different orgs
- Slug uniqueness collision test (force collisions) passes

## Documentation
- docs/story-0002-implementation-walkthrough.md
- docs/story-0002-flow-diagram.md
- docs/story-0002-uat-testing-guide.md
- docs/story-0002-uat-signoff-checklist.md
- docs/story-0002-monitoring-guide.md
- docs/story-0002-signoff-complete.md

## Definition of Done
- All Acceptance Criteria pass
- Migration has rollback path and is tested on SQLite and SQL Server
- Lints/tests pass; docs updated; shard citations present in PR


