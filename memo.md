# Architecture Review Memo — v2 Implementation

Status: Draft (Architect)
Date: 2025-09-20

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/03-billing-go-live.md`, `docs/shards/04-auth-rbac.md`, `docs/shards/05-devops-migrations.md`
Cross-docs: `docs/architecture/v2-architecture.md`, `docs/prd/v2-prd.md`

## 1) Service Boundaries
- Auth/Identity: sessions, memberships, org context; emits audit.
- Domain Verification: email token issuance, inbound processing, DMARC/SPF/DKIM validation, conflict workflow, proof capture.
- Catalog/Entitlements: SKU catalog, plans, org entitlements, business model assignments; audit all changes.
- Metering Ingest: idempotent event intake (`request_id`), queue, late-arrival tolerance, replay.
- Pricing Engine & Estimator: shared pricing rules; deterministic previews; cached estimates.
- Ledger/Settlement: ledger writes, PoR splits, real-time payouts (threshold) and weekly sweeps, reversals for refunds.
- Group/Hierarchy: org tree closure table, billing accounts, allocations, group roles.

## 2) Data Contracts (Summary)
- Tenancy: `organization`, `user`, `membership` (org-scoped roles, pending status).
- Domain Claims: `domain_claim` (DMARC-aligned, wildcard guardrails), invite uniqueness.
- Channel: `partner_of_record`, `commission_rate`, `ledger`.
- Entitlements: `business_model`, `plan`, `product_sku`, `plan_sku`, `org_entitlement`, `org_business_model`.
- Metering: `metering_event`, `pricing_estimate` cache.
- Enterprise: `org_hierarchy` closure, `billing_account`, `org_billing_mapping`, optional `cost_center`, `group_role_membership`.

## 3) Idempotency & Reconciliation
- Ingest idempotency: enforce unique `request_id` (upsert/no-op on duplicate) with durable queue.
- Pricing/Charges: deterministic, replay-safe; no side effects in Estimator; engine guarded with dedupe keys.
- Reconciliation: nightly compare provider logs (email/SMS) vs `metering_event`/`ledger`; produce deltas and alerts.

## 4) Budgets/Caps Enforcement Points
- At action initiation (e.g., before SMS/email send) via Provider Abstraction.
- In Pricing Engine when evaluating overages; block or flag when cap reached with Admin override.
- Group budgets: enforce tighter constraint between billing account budget and per-org cap.

## 5) Provider Abstraction Design
- Adapter interfaces per provider type (email, SMS, validation); inject via configuration.
- Outbound calls signed and idempotent with retry/backoff; dead-letter on persistent failures.
- Webhooks verified (HMAC), retried with exponential backoff, and audited.
- Fallback queues to avoid user-facing latency spikes; replay supported.

## 6) 90-Day Phased Rollout
- Phase 1 (Weeks 1–4):
  - Ship Domain Claims (email) + PoR/Ledger base. Migrations 01–02.
  - Build Estimator read path; seed SKUs/plans; Admin model/plan assignment UI (read-only diffs).
  - Hard feature flags; staging shadow traffic for email verifications.
- Phase 2 (Weeks 5–8):
  - Business Model & Entitlements live (03); Pricing Engine + Estimator parity harness.
  - Metering ingest (04) with queue + idempotency; nightly reconciliation reports.
  - Budgets/caps enforcement at action adapters; basic alerts.
- Phase 3 (Weeks 9–12):
  - Group hierarchy + billing accounts (05); consolidated billing views; PoR precedence.
  - Assist Mode + audit; domain delegation UX.
  - Performance hardening; DR tests; partner dispute tooling MVP.

## 7) Risks & Mitigations
- Metering drift → reconciliation & anomaly alerts; deterministic pricing; request_id guarantees.
- Email spoofing → DMARC alignment, header hash proofs, strict validation paths.
- Partner disputes → PoR precedence rules, immutable audit, reversible ledger entries.
- Cost spikes → budgets, caps, prepaid credits, throttling on action adapters.
- Data model churn → Alembic forward-only plan with safe downgrades; shadow tables for complex moves.

## 8) Observability
- Metrics: queue depth, idempotency hit rates, reconciliation mismatches, budget-threshold hits.
- Tracing: propagate `X-Request-ID`; span around provider calls and pricing.
- Logging: structured JSON; redact PII; audit sensitive changes with actor, target, before/after.
