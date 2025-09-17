# Monitoring & Feedback Plan

Purpose: ensure reliability for the public form, correctness for billing, and continuous UX improvement.

## Service SLOs (initial)
- Public Form Availability: 99.9% monthly
- Public Form p95 Submit Latency: < 800 ms
- Webhook Processing p95: < 2 s; Error Rate < 0.5%
- Email Verification Delivery Success: > 98%
- Builder TTI: < 2.5 s; Interactions at 60 fps target

## Metrics & Alerts
- Backend (Prometheus/OpenTelemetry metrics)
  - http_request_duration_seconds{route} (p50/p95/p99), http_requests_total{status}
  - webhook_events_total{type,result}, webhook_processing_seconds
  - entitlement_checks_total{allowed}, entitlement_check_latency_seconds
  - db_pool_in_use, db_errors_total
  - auth_events_total{kind=signup,verify,reset}, email_bounce_total
- Billing
  - payments_started_total, payments_succeeded_total, payments_failed_total
  - entitlements_created_total, entitlement_lag_seconds (payment→entitlement)
  - recon_discrepancies_total (usage/entitlements vs invoices)
- Public Form
  - submissions_total{mode=test|prod}, rejected_total{reason=not_entitled|not_event_day}
  - client_submit_latency_ms (Real User Monitoring optional)
- Builder (Web Vitals/RUM)
  - TTFB, FCP, LCP, INP; custom: property_panel_update_ms
- Alerts (suggested)
  - Webhook error rate > 2% over 5m
  - Entitlement lag p95 > 30s over 15m
  - Public form p95 latency > 1.5s over 15m
  - Email verification bounce rate > 5% daily

## Observability
- Tracing: OpenTelemetry SDK on FastAPI and Stripe/email clients; propagate `X-Request-ID`
- Logging: structured JSON with `request_id`, `org_id`, `event_id`, `form_id`; redact PII
- Health: `GET /healthz` (liveness), `GET /readyz` (readiness)

## Dashboards
- Ops: latency, error rates, db health, health checks
- Billing: payments funnel, entitlements created, recon discrepancies
- Public Form: submissions, rejects, latency, active events by timezone
- Auth/Email: verification requests/success, password resets, bounces
- Builder Perf: Web Vitals, interaction metrics

## Product Analytics (privacy‑aware)
- Tooling: PostHog/Amplitude (self‑hosted optional) or simple event log
- Events (key)
  - auth_signup_started/completed, email_verified
  - event_created/edited
  - form_created/edited
  - builder_preview_opened, builder_test_submission
  - production_enablement_started/succeeded
  - extend_days_started/succeeded
  - public_submission_succeeded/failed{reason}
- Include: user_id, org_id, event_id, form_id, timezone; never raw PII

## Feedback Loops
- In‑app feedback widget (CSAT after publish, optional NPS later)
- Bug report dialog with console/log attach (privacy‑filtered)
- Support runbook and contact surfaced in errors and docs

## Data Retention
- Metrics: 14–30 days (ops), 90 days (product analytics)
- Logs: 14 days (app), 90 days (audit: publish/delete/CSV/billing)
- Respect deletion/archival policies; avoid storing lead PII in logs/analytics
