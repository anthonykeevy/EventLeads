> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0011 — Text Object

Status: Draft
Epic: M3 — Visual Builder MVP (Hero Feature)
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Implement a simple Text object to establish the DB-first object pattern and builder integration.

## Acceptance Criteria
1) Table `TextField` with fields for content, font, size, color, alignment; FK to canvas object.
2) Registry entry for `text`; palette item visible if enabled.
3) Builder can add/edit/remove Text; properties persisted; runtime renders accurately.

## Definition of Done
- Migration with downgrade; seed registry; UI/editor implemented; tests; docs with shard citations.
