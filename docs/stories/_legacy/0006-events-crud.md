> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0006 — Events CRUD (Org-Scoped)

Status: Draft
Epic: M2 — Events, Forms (Draft), CanvasLayout, Field Types
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#migration-notes-v0.2
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples

## Context
Implement Event CRUD with timezone and start/end dates to support billing readiness and dashboard visibility. Include soft-delete and restore (Admin-only).

## Acceptance Criteria
1) POST /api/v1/events {name, timezone, start_date, end_date} → 201 with status=Draft, soft-delete defaults.
2) GET /api/v1/events returns only caller’s org events ordered by created_at desc.
3) GET/PUT /api/v1/events/{id} enforces org isolation; validates timezone and date range.
4) DELETE /api/v1/events/{id} marks soft delete; POST /api/v1/events/{id}/restore restores (Admin-only).
5) Helpful indexes for events by org and date ranges.

## Definition of Done
- Migration with downgrade; endpoints implemented with RBAC; tests; docs updated with shard citations.
