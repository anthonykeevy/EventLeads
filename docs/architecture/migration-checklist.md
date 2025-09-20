# Migration Safety Plan & Staging Verification Checklist (v2)

Status: Active
Date: 2025-09-20

Shard refs: `docs/shards/05-devops-migrations.md`, `docs/shards/02-data-schema.md`

## Alembic Order (Confirmed)
1. Domain Claims (email) — `20250920_01_domain_claims_email.py`
2. PoR & Ledger — `20250920_02_por_commission_ledger.py`
3. Business Model & Entitlements — `20250920_03_business_model_entitlements.py`
4. Metering Events — `20250920_04_metering_events.py`
5. Org Hierarchy & Billing Accounts — `20250920_05_org_hierarchy_and_billing_accounts.py`

## Safety Strategy
- Forward-only migrations with explicit `downgrade()` best-effort rollbacks.
- Data migrations idempotent and chunked; wrap in transactions where supported.
- Pre-flight checks: ensure no conflicting data (e.g., duplicate domains) before unique constraints.
- Default seeds behind feature flags; no hard activation on upgrade.
- Real-time PoR split threshold set via config (AUD 50); safe default.

## Dual-Write / Shadow Strategy (if needed)
- For Pricing Engine rollout: write estimates to `pricing_estimate` and run engine in shadow mode, comparing outputs; no ledger writes until parity achieved.
- For Metering: accept events, enqueue, and store shadow copies with reconciliation tags; replay test in staging.

## Staging Verification Checklist
- Domain Claims
  - Create claim → verify DMARC aligned path → status transitions audited.
  - Conflict flow triggers `pending_conflict` and escalation path.
- Invitations
  - Uniqueness (`UNIQUE(org_id, lower(email))`) enforced; TTL and daily caps from GlobalSetting.
- Entitlements
  - Seed SKUs/plans; assign model/plan; verify `plan_sku` included/overage/tiers.
- Estimator vs Engine
  - 10 SKU matrix parity within tolerance; cache hit/miss behavior acceptable.
- Metering
  - Idempotency on duplicate `request_id`; DLQ flow; replay produces same ledger.
- Ledger/Settlement
  - Real-time split ≥ threshold; weekly sweep on small lines; reversals tested.
- Group Billing
  - Hierarchy closure; cycle-safety on move; consolidated invoice with PoR precedence.
- Observability
  - Metrics exposed; traces present; audit logs complete and redaction verified.
