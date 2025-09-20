> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0005 — Dashboard Scaffold

Status: Draft
Epic: M1.5 — Dashboard Scaffold
Owners: Frontend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples

## Context
Provide a guided, org-scoped dashboard that serves as the hub: create org (if none), invite teammates, create event, and see recent activity. Data is sourced from the database and indexed for performance.

## Acceptance Criteria
1) Empty state: prompts to Create Organization (if none), Invite teammates, Create Event.
2) Populated state: lists recent Events and Forms with counts and upcoming dates; quick actions visible.
3) Org isolation enforced; performance acceptable (paged queries, proper indexes).

## Definition of Done
- UI implemented with protected routes; basic tests; shard citations included in PR.
