> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0010 — Visual Builder MVP (Desktop)

Status: Draft
Epic: M3 — Visual Builder MVP (Hero Feature)
Owners: Frontend, Backend

Shard Citations:
- docs/shards/02-data-schema.md#tables

## Context
Deliver the core builder: desktop canvas, selection, grid snapping, properties, and background image, powered by DB-backed objects.

## Acceptance Criteria
1) Canvas render, selection, move/resize with grid snapping and bounds.
2) Properties panel: label, export label, required, color, box styling; persisted to DB.
3) ObjectType registry drives palette and editors.
4) Background image upload + color fallback; stored and rendered.
5) Device preview with fallback to Desktop when missing.

## Definition of Done
- UI and persistence implemented; tests for persistence/restore; docs updated with shard citations.
