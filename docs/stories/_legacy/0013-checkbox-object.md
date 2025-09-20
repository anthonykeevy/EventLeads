> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0013 — Checkbox Object

Status: Draft
Epic: M3 — Visual Builder MVP (Hero Feature)
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Add Checkbox object with persisted checked state and label, following the DB-first extensibility pattern.

## Acceptance Criteria
1) Table `CheckboxField` with label, default_checked.
2) Registry entry for `checkbox`; palette item visible if enabled.
3) Builder can add/edit/remove Checkbox; persisted; runtime renders and validates.

## Definition of Done
- Migration with downgrade; seeds; UI/editor implemented; tests; docs with shard citations.
