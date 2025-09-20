> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0007 — Forms CRUD (Draft Only, No Slug)

Status: Draft
Epic: M2 — Events, Forms (Draft), CanvasLayout, Field Types
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples

## Context
Allow multiple Form drafts per Event for exploration and review. Do not issue `public_slug` yet; that is generated later after builder output when the form is Ready/Published.

## Acceptance Criteria
1) POST /api/v1/events/{event_id}/forms {name} → 201 with status=Draft, soft-delete defaults.
2) GET /api/v1/events/{event_id}/forms lists org-scoped forms for the event.
3) GET/PUT /api/v1/forms/{id} enforces org isolation.
4) DELETE /api/v1/forms/{id} soft-deletes; POST /api/v1/forms/{id}/restore restores (Admin-only).

## Definition of Done
- Migration (if needed) with downgrade; endpoints and UI list/create; tests; docs with shard citations.
