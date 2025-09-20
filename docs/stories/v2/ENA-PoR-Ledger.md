# ENA-PoR-Ledger

Type: Enabler
Status: Pending
Epic: Foundations
Links.requires: []
ADR refs: `docs/adr/ADR-001-PartnerOfRecord-and-Commissions.md`
Cross-docs: `docs/prd/v2-prd.md` (Channel & Commissions), `docs/architecture/v2-architecture.md` (Ledger/Settlement)

## Description
Implement Partner-of-Record (PoR), commission rates, and ledger with real-time splits ≥ threshold and weekly sweeps for smaller lines, with disputes and reversals.

## Acceptance Criteria
1. PoR assignment lifecycle managed; status changes audited.
2. Commission rates applied per partner tier and SKU; unit tests cover edge cases.
3. Real-time split for lines where `amount_gross ≥ AUD 50` (configurable); weekly sweep for others.
4. Reversals supported; disputes tracked; settlement idempotent.
5. Consolidated billing reflects PoR precedence rules at billing account level.
