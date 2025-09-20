> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0008 — CanvasLayout Bootstrap (Desktop Required)

Status: Draft
Epic: M2 — Events, Forms (Draft), CanvasLayout, Field Types
Owners: Backend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Initialize the first CanvasLayout for each Form. Desktop is required; Tablet/Mobile optional. Runtime must fall back to Desktop when device-specific layout is unavailable.

## Acceptance Criteria
1) POST /api/v1/forms/{id}/layouts {device_type, aspect_ratio, resolution_x, resolution_y} → 201 with `revision_number=1`.
2) FK enforces `form_id` relationship. Unique constraint on (form_id, device_type) for current layout.
3) Default device is Desktop; enforce presence before publish.

## Definition of Done
- Migration with downgrade; endpoint implemented; tests; docs with shard citations.
