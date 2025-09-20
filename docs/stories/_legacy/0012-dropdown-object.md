> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0012 — Dropdown Object

Status: Draft
Epic: M3 — Visual Builder MVP (Hero Feature)
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Add Dropdown object with options and default selection, following the same DB-first extensibility pattern.

## Acceptance Criteria
1) Tables `DropdownField` and `DropdownOption` (ordered, label, value, is_default).
2) Registry entry for `dropdown`; palette item visible if enabled.
3) Builder editor for options add/edit/reorder; persisted; runtime renders/selects default.

## Definition of Done
- Migration with downgrade; seeds; UI/editor implemented; tests; docs with shard citations.
