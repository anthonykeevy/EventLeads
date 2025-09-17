# Risk Register (MVP)

Severity = Likelihood × Impact (Low/Medium/High). Owner = DRI for mitigation.

| ID | Risk | Likelihood | Impact | Severity | Mitigation | Owner | Trigger/Monitor |
| -- | ---- | ---------- | ------ | -------- | ---------- | ----- | --------------- |
| R1 | Event‑day timezone miscalc bills wrong days | Med | High | High | Unit tests for tz windows; unique UsageCharge per day; recon job | Eng Lead | Errors in tz calc; duplicate/missed charges |
| R2 | Webhook idempotency errors cause double/failed posting | Med | High | High | Verify signature; store processed event IDs; idempotent processing | Backend | Stripe retries; log alerts |
| R3 | Email deliverability blocks onboarding | Med | Med | Med | Verified sender domain; bounce handling; resend cooldown/max per day | DevOps | Bounce rate; verification failure rate |
| R4 | Public form abuse/spam inflates usage | Med | Med | Med | Rate limiting; optional CAPTCHA; IP heuristics; anomaly alerts | Backend | Sudden spike in submissions |
| R5 | Builder performance <60fps | Med | Med | Med | Virtualize; memoize; throttle; move heavy work off main thread | Frontend | Perf CI; runtime FPS sampling |
| R6 | Preview vs production render drift | Low | High | Med | Single render path; immutable snapshot; regression tests | Frontend | Snapshot diffs; bug reports |
| R7 | Data model churn (FormID migration) | Med | Med | Med | Alembic backfill; feature flags; rollback plan | Backend | Migration failures |
| R8 | Permissions gaps expose actions to Users | Low | High | Med | Route guards; UI disables; audit logs; tests against matrix | Eng Lead | Access logs; audit anomalies |
| R9 | CSV exports leak PII | Low | High | Med | Admin‑only; audit CSV exports; signed URLs expire | Backend | Export spikes; audit alerts |
| R10 | Offline form queue loss/duplication | Low | Med | Low | Client IDs; server idempotency; queue size limits | Frontend | Sync error metrics |
| R11 | Invoice/usage reconciliation mismatch | Med | Med | Med | Nightly recon; discrepancy report; manual adjustment flow | Finance | Recon report deltas |
| R12 | Accessibility regressions | Med | Med | Med | AXE checks; manual audits; AC in stories | QA | Accessibility CI failures |

Notes
- See `docs/webhooks-stripe.md` for webhook/idempotency; `docs/billing-config.example.yaml` for pricing.
- Audit log critical events: publish, archive/delete/restore, role changes, CSV export, billing operations.

