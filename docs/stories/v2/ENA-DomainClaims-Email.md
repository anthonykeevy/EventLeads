# ENA-DomainClaims-Email

Type: Enabler
Status: InProgress
Epic: Foundations
Links.requires: []
ADR refs: `docs/adr/ADR-002-DomainClaims-Email-Verification.md`
Cross-docs: `docs/prd/v2-prd.md` (Domain Claims, Privacy & Discovery), `docs/architecture/v2-architecture.md` (Domain Verification Service)

## Description
Email-based domain claim verification aligned with DMARC. Multi-domain per org, wildcard only post root verify with Owner + 2FA, conflict workflow, and audit. No member identity leakage.

## Acceptance Criteria
1. Admin can submit email challenge for a domain; system validates DKIM/SPF and DMARC alignment; `domain_claim.status` transitions `pending → verified` on success.
2. Proof artifacts stored hashed in `domain_claim.proof`; no PII leakage.
3. Conflict sets `status = pending_conflict` and exposes escalation path; actions audited (actor, before/after).
4. Wildcard toggle disabled until root verified and Owner + 2FA confirmed; enabling writes `wildcard = true` with audit.
5. Invitation uniqueness enforced: `UNIQUE(org_id, lower(email)) WHERE consumed_at IS NULL`.
6. Privacy-safe join: if signup email domain matches a verified claim, show CTA to Request to Join; member identities never shown.

## Out of Scope
- Partner Directory (P2).
