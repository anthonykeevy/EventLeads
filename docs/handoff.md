# Handoff Guide

This guide consolidates what an engineering team needs to start building and operating the MVP.

## Documents Index
- PRD: `docs/event-form-prd.md`
- UI/UX Spec: `docs/front-end-spec.md`
- Architecture: `docs/tech-architecture.md`, `docs/tech-architecture-v0.2.md`
- Data Schema: `docs/shards/02-data-schema.md`, `docs/event-form-database.sql`
- Billing: `docs/shards/03-billing-go-live.md`, `docs/billing-config.example.yaml`, `docs/webhooks-stripe.md`
- Auth/RBAC: `docs/shards/04-auth-rbac.md`, `docs/permissions-matrix.md`, `docs/email-config.md`
- Roadmap: `docs/roadmap.md`; Risks: `docs/risk-register.md`
- Setup: `docs/setup.md`
- Entitlements API: `docs/api-entitlements.md`

## Runbook (Dev)
1) Environment & deps: see `docs/setup.md`
2) DB migrations: generate/apply Alembic scripts for v0.2/v0.3 schema changes
3) Stripe: configure test keys and webhook
4) Email: configure local SMTP or provider

## Release Checklist (MVP)
- [ ] Migrations applied (v0.2 + v0.3 entitlements)
- [ ] Auth flows verified (signup/verify/reset)
- [ ] Builder v1 interactions meet performance targets
- [ ] Preview == Production render parity
- [ ] Status gating requires successful test submission
- [ ] Production enablement charges create entitlements
- [ ] Event-day guard enforces entitlements (tz-correct)
- [ ] Leads list/filters; CSV export Admin-only
- [ ] RBAC enforcement matches `docs/permissions-matrix.md`
- [ ] Onboarding wizard shown/dismissible
- [ ] Soft deletes & restore work
- [ ] Health endpoints and basic observability in place

## Operational Notes
- Webhooks are idempotent; store processed event IDs
- Audit log critical actions: publish, delete/restore, role changes, CSV export, billing
- Recon: nightly usage/entitlement vs invoices

## Contacts & Ownership
- Product Owner: decisions on scope and pricing
- Eng Lead: migrations, webhooks, billing enforcement
- Frontend Lead: builder performance, accessibility
- QA: AXE checks, tz/billing tests, RBAC scenarios

---

## DB Accounts & Roles (Dev)

- Seeded Roles: SystemAdmin, Admin, User
  - SystemAdmin: full platform administration (Permissions: {"all": true})
  - Admin: org administration, billing, CSV export (Permissions: {"org_admin": true, "billing": true, "csv_export": true})
  - User: org view, edit non‑production forms (Permissions: {"org_view": true, "edit_non_production": true})

- Seeded Users (dev only; passwords stored in env, not documented here):
  - sysadmin@local.dev → SystemAdmin
  - admin@local.dev → Admin
  - user@local.dev → User

- Environment variables (no secrets exposed here):
  - `SEED_SYSADMIN_EMAIL`, `SEED_SYSADMIN_PASSWORD`
  - `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`
  - `SEED_USER_EMAIL`, `SEED_USER_PASSWORD`

- Connection (dev):
  - `DATABASE_URL=mssql+pyodbc://@localhost/EventTrackerDB_Dev?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes`
  - Adjust for non‑Windows by using SQL auth or Azure AD auth.

- Verification queries (T‑SQL):
  - `SELECT RoleID, RoleName, IsSystemRole, Permissions FROM Role ORDER BY RoleID;`
  - `SELECT TOP 10 UserID, Username, Email, RoleID FROM [User] ORDER BY UserID DESC;`
  - `SELECT ur.UserID, ur.RoleID FROM UserRole ur;`

- Security notes:
  - These dev users are for local testing; rotate or disable for shared environments.
  - Use least‑privilege SQL logins in QA/Prod; do not reuse dev credentials.
