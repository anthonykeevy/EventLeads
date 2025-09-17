# Technical Architecture v0.2 Addendum

This addendum complements `docs/tech-architecture.md` with updates required by the latest UI/UX and PO validation.

## API Base, Health, and Middleware

- Base path: `/api/v1`
- Health: `GET /healthz` (liveness), `GET /readyz` (readiness)
- Middleware:
  - Request ID + structured logging
  - Error envelope with trace ID (Problem Details)
  - CORS for app and public form origins
  - Rate limiting for auth-sensitive endpoints

## Auth Flows: Email Verification & Password Reset

- Email Verification
  - Table: `EmailVerificationToken(user_id, token, expires_at, consumed_at)`
  - Flow: signup -> send token link -> verify -> activate account -> redirect dashboard
  - Resend: cooldown (e.g., 60s) and daily cap
- Password Reset
  - Table: `PasswordResetToken(user_id, token, expires_at, consumed_at)`
  - Flow: request -> email link -> set new password -> invalidate sessions
- Security
  - Tokens random 32+ bytes, one-time, expire in 30â€“60 min
  - Audit issuance and consumption; rate limit endpoints

## Environment Variables

Provide `.env.dev`, `.env.test`, `.env.prod`. Example keys are in `.env.example`:

```
APP_BASE_URL=
JWT_SECRET=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASS=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
DB_DSN=
DEFAULT_TIMEZONE=UTC
```

## Billing Enforcement

- Event-day guard: compute "today" in `Event.timezone`; block submissions outside `[start_date, end_date]`
- Usage charges: on first production submission per day, insert `UsageCharge(event_id, charge_date, amount)` per schedule
- Invoicing: sum usage into invoices; handle via Stripe and webhooks

## Schema Summary (v0.2)

- Event: add `timezone`, `end_date`, soft deletes
- New: `Form(id, event_id, name, status, public_slug, soft-delete)`
- CanvasLayout: add `form_id` (deprecate `event_id`)
- Lead: add `is_test`, `form_id`, soft-delete metadata
- New: `UsageCharge(org_id, event_id, charge_date, amount, source)` unique per day

## Bootstrap & Seeding

- Seed `ObjectType`: TextField, DropdownField, Checkbox (see `docs/event-form-database.sql` v0.2 section)
- Admin bootstrap: create first Organization and Admin user on first run if none exist
- Provide `scripts/bootstrap_dev.py` (future) to initialize dev environment

---

## Observability & Monitoring (v0.2)

### Metrics & Tracing
* Expose Prometheus `/metrics`; instrument HTTP, DB, webhooks, entitlements
* Emit OpenTelemetry traces; propagate `X-Request-ID`

### Dashboards & Alerts
* Dashboards: Ops, Billing, Public Form, Auth/Email, Builder Perf
* Alerts: webhook error spikes, entitlement lag, public form latency, email bounce rate

### Logging & Audit
* Structured JSON with `request_id`, `org_id`, `event_id`, `form_id`; redact PII
* Audit actions: publish, archive/delete/restore, role changes, CSV exports, billing

### Product Analytics
* Track privacy-aware events (publish, extend days, submissions) with minimal metadata



