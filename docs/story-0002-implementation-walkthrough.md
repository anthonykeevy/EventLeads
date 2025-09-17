# Story 0002 — Event & Form Foundation: Implementation Walkthrough

Status: In Progress
Related: docs/stories/0002-event-form-foundation.md
Shard refs: docs/shards/02-data-schema.md, docs/shards/04-auth-rbac.md, docs/shards/05-devops-migrations.md

## Scope Recap
- Event CRUD with timezone, start/end date, soft delete
- Form CRUD under Event with unique PublicSlug
- CanvasLayout create for device layouts (revision 1)

## Backend Changes
- Models
  - Event: added fields Timezone, StartDate, EndDate; soft-delete (IsDeleted, DeletedAt, DeletedBy)
  - New: Form (Name, Status, PublicSlug, soft-delete, audit fields)
  - New: CanvasLayout (DeviceType, AspectRatio, ResolutionX/Y, RevisionNumber, soft-delete)
- Routers (org-scoped via JWT; Admin-only delete/restore)
  - events: list/create/get/update/delete/restore
  - forms: list/create/get/update/delete/restore (scoped to Event)
  - canvas: create layout for a given Form
- Migrations
  - a014_canvaslayout_table (new table)
  - Type alignment and guards added to earlier migrations for idempotence across environments

## Endpoints
- GET /api/v1/events — list org events
- POST /api/v1/events — create event
- GET /api/v1/events/{id} — get event
- PUT /api/v1/events/{id} — update event
- DELETE /api/v1/events/{id} — soft delete (Admin)
- POST /api/v1/events/{id}/restore — restore (Admin)
- GET /api/v1/events/{id}/forms — list forms
- POST /api/v1/events/{id}/forms — create form with unique slug
- GET /api/v1/events/{id}/forms/{form_id} — get form
- PUT /api/v1/events/{id}/forms/{form_id} — update form
- DELETE /api/v1/events/{id}/forms/{form_id} — soft delete (Admin)
- POST /api/v1/events/{id}/forms/{form_id}/restore — restore (Admin)
- POST /api/v1/canvas/forms/{form_id}/layouts — create layout

## Auth & Org Scoping
- All endpoints require JWT; org_id from token scopes queries (docs/shards/04-auth-rbac.md)
- Admin-only actions: delete/restore for Events and Forms

## Notes & Constraints
- PublicSlug uniqueness enforced and collision-handled (max 80 chars)
- SQL Server-specific filtered indexes; migrations guard missing tables and type mismatches
- Booleans use BIT per data standards (docs/shards/02-data-schema.md)
