# ADR-001: Partner of Record (PoR) and Commissions

Status: Accepted
Date: 2025-09-20

## Context
We need a channel model supporting Platform-owned sales with Partner-of-Record (PoR) assignments, real-time commission splits on qualifying lines, weekly sweeps for smaller lines, deal registration, referral codes, and auditable dispute handling.

## Decision
- Adopt Platform-owned channel with PoR as default when present.
- Settlement:
  - Real-time split for qualifying ledger lines where gross amount ≥ configured threshold.
  - Default threshold: AUD $50 per ledger line (configurable).
  - All other lines are swept weekly.
- Data model:
  - `partner_of_record(org_id, partner_id, start_at, end_at? null, status)`; primary key `(org_id, partner_id, start_at)`.
  - `commission_rate(partner_tier, sku, pct)`.
  - `ledger(entry_id, org_id, project_id?, sku, quantity, amount_gross, partner_pct, partner_amount, net, status, created_at)`.
- Auditing for PoR assignments, commission rate changes, and settlements.
- Disputes: status tracked and reversible ledger entries supported.

## Consequences
- Requires accurate PoR assignment and tiered commission rates management.
- Real-time path must be resilient and idempotent; weekly sweep must reconcile deltas.
- Dispute tooling and audit trails are mandatory to preserve partner trust.

## References
- PRD v2: Business Models, Channel Model & Commissions
- Architecture v2: Ledger/Settlement service, Channel & Commissions data contracts
- Threshold configuration: `AUD 50` default for real-time splits

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/05-devops-migrations.md`

## Risks
- Incorrect PoR precedence could misroute commissions; implement unit + integration tests around overrides.
- Real-time split failures could leave unsettled lines; implement retry with DLQ and weekly sweep fallback.

## Rollback Strategy
- Disable real-time splits via feature flag; revert to weekly sweeps only.
- Reverse ledger entries for any incorrect settlements; preserve audit trail.

