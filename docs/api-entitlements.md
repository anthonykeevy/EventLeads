# Entitlements API (Prepaid Event Days)

Admin-only endpoints unless noted. All paths are prefixed with `/api/v1`.

## List Entitlements
- `GET /events/{event_id}/entitlements`
- Query: `from` (YYYY-MM-DD, optional), `to` (YYYY-MM-DD, optional)
- Returns: array of `{ date, amount_cents, invoice_id }`

## Quote Selected Days
- `POST /events/{event_id}/entitlements/quote`
- Body: `{ dates: [YYYY-MM-DD], currency?: 'USD' }`
- Returns: `{ items: [{ date, amount_cents }], subtotal_cents, currency }`

## Start Checkout for Selected Days
- `POST /events/{event_id}/entitlements/checkout`
- Body: `{ dates: [YYYY-MM-DD], success_url, cancel_url }`
- Returns: `{ checkout_url }`
- Behavior: Creates a Stripe Checkout Session or Payment Intent with metadata: `event_id`, `dates`.
- Note: Entitlements are created by the webhook after successful payment.

## Validate Access (Public)
- `GET /public/events/{event_id}/access`
- Query: `date` (YYYY-MM-DD, optional; defaults to "today" in event timezone)
- Returns: `{ allowed: boolean, next_available_date?: YYYY-MM-DD }`
- Usage: Public form pre-check before enabling submit.

## Admin Reactivation
- `POST /events/{event_id}/reactivate`
- Body: `{ dates: [YYYY-MM-DD] }` (alias of checkout for UX convenience)
- Returns: `{ checkout_url }`

## Webhook Processing (Stripe)
- `POST /webhooks/stripe`
- On payment success:
  - Create `EventDayEntitlement` rows per purchased day
  - Link to invoice
  - If purchase was for initial enablement, set Form/Event status to `ProductionEnabled`

## Authorization & Errors
- Requires `role=Admin` except for `/public/...` endpoint.
- 403 if non-Admin calls admin routes; 422 if dates outside event window; 409 on duplicate dates.
- All responses include `request_id` for traceability.

