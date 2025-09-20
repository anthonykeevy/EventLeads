> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0015 — Publish & Stripe Billing (MVP)

Status: Draft
Epic: M5 — Publish & Stripe Billing (MVP)
Owners: Backend, DevOps, Frontend

Shard Citations:
- docs/shards/03-billing-go-live.md
- docs/shards/05-devops-migrations.md#alembic-flow
- docs/shards/02-data-schema.md#tables

## Context
Enable Admins to publish forms, enforce the event-day guard, charge on first production submission per day, and integrate Stripe with idempotent webhooks and invoice rollup.

## Acceptance Criteria
1) Admin-only Publish endpoint; enforce Desktop layout present and Ready; event-day guard computed in event timezone.
2) On first production submission per day, write `UsageCharge(event_id, charge_date, amount)` per schedule; unique per day; visible in invoices.
3) Stripe: create PaymentIntent/Checkout as needed; webhook handlers (success/failure) idempotent; update invoice records.

## Definition of Done
- Migrations for `UsageCharge`/invoices; webhook secrets/config; tests for guard and idempotency; docs with shard citations.
