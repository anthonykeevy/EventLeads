# ADR-002: Domain Claims via Email Verification (DMARC-aligned)

Status: Accepted
Date: 2025-09-20

## Context
Organizations need to claim domains using email-based verification that aligns with DMARC and preserves privacy. Support multi-domain per org, wildcard after root verify with guardrails, and conflict workflows.

## Decision
- Implement email-based domain claims with DMARC alignment. Store proof artifacts (headers hashed) to prevent PII leaks.
- Table `domain_claim`:
  - `claim_id uuid pk`, `org_id fk`, `domain citext`,
  - `status ENUM('pending','verified','revoked','pending_conflict')`,
  - `verified_at timestamptz null`, `wildcard bool default false`, `proof jsonb`,
  - `UNIQUE(domain) WHERE status IN ('pending','verified')`.
- Invitation uniqueness: `UNIQUE(org_id, lower(email)) WHERE consumed_at IS NULL`.
- Wildcard allowed only after root domain verified, Owner role, and 2FA.
- Conflict workflow: mark `pending_conflict`, escalate, and resolve with audit.

## Consequences
- Email challenge service must validate DMARC alignment and store non-sensitive proofs.
- Join requests must not leak member identities; provide privacy-safe hints only.
- Adds admin guardrails and audit requirements for wildcard enablement.

## References
- PRD v2: Domain Claims & Privacy/Discovery
- Architecture v2: Domain Verification Service, Tenancy & Identity

Shard refs: `docs/shards/04-auth-rbac.md`, `docs/shards/02-data-schema.md`

## Risks
- Email spoofing or misaligned headers could allow false positives; mitigate with strict DMARC alignment and proof hashing.
- Overly aggressive wildcard could expand scope unintentionally; require Owner + 2FA and admin review.

## Rollback Strategy
- Revoke claims by setting status to `revoked` and removing wildcard flags; maintain audit trail.
- Temporarily disable wildcard issuance via configuration and restrict to root verification only.

