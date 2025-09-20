# ENA-Metering-Service

Type: Enabler
Status: Pending
Epic: Foundations
Links.requires: []
ADR refs: `docs/adr/ADR-004-Consumption-Metering-and-Pricing.md`
Cross-docs: `docs/prd/v2-prd.md` (Consumption Billing & Estimator), `docs/architecture/v2-architecture.md` (Metering Ingest, Pricing Engine)

## Description
Implement idempotent metering ingest with durable queue and replay; Pricing Engine and Estimator using shared rules; budgets/caps enforcement at adapters and engine.

## Acceptance Criteria
1. `/metering/events` accepts batches; enqueues with idempotency on `request_id`; duplicate yields 409 or safe no-op.
2. Nightly reconciliation compares provider logs to `metering_event`/`ledger`; emits deltas and alerts.
3. Estimator parity harness validates pricing vs engine across 10‑SKU matrix.
4. Budgets/caps enforced both at action initiation (email/SMS) and during pricing evaluation; admin override path exists.
