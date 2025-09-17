# Stripe Webhooks & Billing Endpoints

## Endpoints

- `POST /api/v1/billing/checkout` (server): starts a checkout/session or triggers charge creation
- `POST /api/v1/webhooks/stripe` (public): receives Stripe events

## Security

- Verify `Stripe-Signature` header with `STRIPE_WEBHOOK_SECRET`
- Use `Idempotency-Key` for outbound Stripe-charge requests
- Store processed event IDs to guarantee idempotent webhook handling

## Events to Handle

- `payment_intent.succeeded`: mark related invoice/usage as paid
- `payment_intent.payment_failed`: mark invoice as failed; notify user
- `charge.refunded` (if refunds supported): update invoice and usage accordingly

## Processing Model

1. Parse and verify event
2. Lookup internal record by metadata (e.g., `event_id`, `organization_id`, `usage_charge_id`)
3. If payment for production enablement succeeded:
   - Create `EventDayEntitlement` rows per purchased day (unique per day)
   - Link entitlements to the invoice; mark Form/Event as ProductionEnabled if this was an enablement payment
4. If already processed (seen event ID), exit 200
5. Append webhook delivery log and return 200 quickly; avoid long blocking work in webhook

## Error Handling & Retries

- On transient errors: respond 2xx, queue internal retry (avoid Stripe retry loop)
- On verification failure: 400 (log and alert)
- Store delivery attempts with timestamps and outcomes

## Refunds & Cancellations

- Policy: allow manual refund for mis-billing; create negative UsageCharge for adjustment
- If refund occurs in Stripe: sync via `charge.refunded` webhook

## Test vs Production

- Use Stripe test keys in dev/test
- Ensure test webhooks are configured per environment
