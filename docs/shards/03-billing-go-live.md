# Billing & Go-Live

Source refs: ../event-form-prd.md

## Spend Rules
- Default budget: $50/day per org
- Buffer windows: 24h main window + 3h grace for settlements

## Publishing Controls
- Only Admin role can publish
- Publish creates an immutable render snapshot

## Invoice Lifecycle
- Draft → Open → Paid/Failed → Archived
 - Stripe as PSP; webhooks update invoice status

## v0.2 Billing Updates
- Day-based pricing per event day:
  - Day 1: $50, Day 2: +$40, Day 3: +$30, Day 4: +$20, Day 5: +$10, Day 6+: +$10/day
- UI shows day-by-day prices and running total before payment.

## v0.3 Prepaid Entitlements (Updated Policy)
- Charge timing: when switching a form to Production Ready.
- Access model: submissions are permitted only on days the customer has purchased (prepaid event days).
- Initial enablement: user selects event date(s) or a range, pays, then status becomes ProductionEnabled.
- Extensions: user can add more days later; purchases create additional entitlements.
- Reactivation: if production was disabled or dates elapsed, purchasing more days re-activates access for those new days only.
- Data model:
  - Create entitlement rows per purchased day: `EventDayEntitlement(org_id, event_id, date, amount, invoice_id)` unique per (event_id, date).
  - Keep `UsageCharge` for accounting/audit if desired; entitlements represent access rights.
- Server enforcement:
  - Public form checks entitlement for `today` in event timezone; block submissions otherwise.
  - Admin UI shows remaining/purchased days; offer "Extend Days" CTA.

## Stripe Configuration
- Use `docs/billing-config.example.yaml` as a template to map Price IDs per environment
- Keep product and price IDs out of code; load from config or env

## Webhooks & Checkout
- Endpoints:
  - `POST /api/v1/billing/checkout` to start payment
  - `POST /api/v1/webhooks/stripe` to process events
- Security:
  - Verify `Stripe-Signature`; use `Idempotency-Key` when creating payment intents
  - Store processed event IDs to ensure idempotency

## Refunds & Cancellations
- Refunds allowed by support; create adjustment (negative) UsageCharge entries and update invoices
- Auto-sync refunds via Stripe webhook `charge.refunded`



