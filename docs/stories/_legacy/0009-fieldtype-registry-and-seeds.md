> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0009 — FieldType Registry & Seeds

Status: Draft
Epic: M2 — Events, Forms (Draft), CanvasLayout, Field Types
Owners: Backend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Introduce a registry for object types used by the Visual Builder and seed the initial types. Enable future per-organization visibility toggles.

## Acceptance Criteria
1) Tables: `FieldType(id, key, name, status)` and `FieldTypeVisibility(field_type_id, org_id, enabled)`.
2) Seed FieldTypes: Text, Dropdown, Checkbox.
3) Service for querying enabled FieldTypes for an org.

## Definition of Done
- Migration with downgrade and seeds; service implemented; docs with shard citations.
