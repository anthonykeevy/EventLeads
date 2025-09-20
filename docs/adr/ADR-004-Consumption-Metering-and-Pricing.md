# ADR-004: Consumption Metering and Pricing

Status: Accepted
Date: 2025-09-20

## Context
Consumption billing requires durable, idempotent metering ingest, deterministic pricing, budgets/caps/alerts, and alignment between preview estimates and billed amounts.

## Decision
- Metering ingest:
  - `metering_event(event_id uuid pk, org_id, project_id, sku, quantity numeric, source ENUM('form_submit','backend','replay'), event_time, request_id unique, metadata jsonb)`.
  - Enforce idempotency via `request_id` and durable queue with replay.
- Pricing Engine & Estimator:
  - Estimator API provides deterministic previews; uses same pricing rules as engine; cached results table `pricing_estimate`.
  - Budgets/caps enforced at engine and at action initiation.
- Settlement writes ledger lines and applies PoR commission splits.

## Consequences
- Requires queue infrastructure and reconciliation jobs.
- Budgets/caps/alerts must be respected by action services (e.g., SMS/email send).
- Replay-safe pricing and idempotent ingest critical for correctness.

## References
- PRD v2: Consumption Billing & Estimator; Budgets/Caps/Alerts
- Architecture v2: Metering Ingest; Pricing Engine; Ledger/Settlement

Shard refs: `docs/shards/03-billing-go-live.md`, `docs/shards/05-devops-migrations.md`

## Risks
- Metering drift or duplicate events; enforce `request_id` uniqueness and reconciliation.
- Pricing rule regressions break parity with estimator; add golden test matrix and shadow runs.

## Rollback Strategy
- Disable engine writes (ledger) and run in read-only shadow mode, keeping estimator live.
- Rewind/replay metering events after rule fixes to correct ledger, with reversals recorded.

