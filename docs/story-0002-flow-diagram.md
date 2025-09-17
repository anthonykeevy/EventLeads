# Story 0002 — Events/Forms/Layouts: Flow Overview

Shard refs: docs/shards/02-data-schema.md, docs/shards/04-auth-rbac.md

## High-Level Sequence
1) User logs in (JWT with org_id, role)
2) Create Event
   - POST /api/v1/events (org-scoped)
   - DB: insert Event (Timezone, StartDate/EndDate, Status=Draft)
3) Create Form under Event
   - POST /api/v1/events/{id}/forms
   - Slug generated (unique, <=80 chars)
4) Create CanvasLayout for Form
   - POST /api/v1/canvas/forms/{form_id}/layouts
   - DB: insert CanvasLayout (DeviceType, AspectRatio, ResolutionX/Y, RevisionNumber=1)
5) Manage lifecycle
   - Update Event/Form (PUT)
   - Soft delete / restore (Admin-only)

## Auth & RBAC Touchpoints
- All endpoints require Bearer JWT
- Org isolation via org_id filters
- Admin-only: delete/restore

## Tables Involved
- Event(EventID, OrganizationID, Name, Status, Timezone, StartDate, EndDate, soft-delete)
- Form(FormID, EventID, Name, Status, PublicSlug, soft-delete)
- CanvasLayout(CanvasLayoutID, FormID, DeviceType, AspectRatio, ResolutionX/Y, RevisionNumber, soft-delete)
