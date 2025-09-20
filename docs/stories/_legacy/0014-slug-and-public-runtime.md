> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0014 — Slug & Public Runtime

Status: Draft
Epic: M4 — Slug & Public Runtime
Owners: Backend, Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples
- docs/shards/05-devops-migrations.md#alembic-flow

## Context
Issue a stable `public_slug` when a form is marked Ready/Published, then serve the public runtime page with submission flow and basic rate limiting.

## Acceptance Criteria
1) Transition Draft → Ready/Published emits a globally unique `public_slug` (retry on collision); persisted; stable.
2) Public route by slug renders latest layout; CORS configured; no auth needed.
3) Submission endpoint validates and stores lead with `is_test` when in test mode; basic rate limit.

## Definition of Done
- Migration (if needed) with downgrade; endpoints and UI implemented; tests; docs with shard citations.
