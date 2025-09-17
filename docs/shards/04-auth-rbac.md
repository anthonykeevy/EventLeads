# Auth & RBAC

Source refs: ../tech-architecture.md

## Roles
- Admin, User

## JWT Claims
- sub (user id), org_id, role, exp, iat

## Frontend Route Guards
- RoleGuard HOC checks `role` claim; redirects to /login on failure

## Backend RBAC Middleware
- Dependency that validates JWT and enforces role per-route using FastAPI dependencies

## Permissions Matrix
- See `docs/permissions-matrix.md` for role capabilities across resources (Events, Forms, Leads, Billing).
- Key rules:
  - Only Admins can publish, archive/delete/restore, and export Leads CSV.
  - Users can view all org events and leads; can edit/add events and forms, but not when a form is `ProductionEnabled`.
  - Public users can only submit production leads via the public link during event dates.

## Routing & Enforcement Examples
- Protect publish endpoint: Admin-only
  - `POST /api/v1/events/{id}/publish` → require `role=Admin`
- CSV export: Admin-only
  - `GET /api/v1/events/{id}/leads.csv` → require `role=Admin`
- Form edits: block when status is ProductionEnabled for non-Admin
  - `PUT /api/v1/forms/{id}` → allow if `role=Admin` or (`role=User` and `status != ProductionEnabled`)

- Soft delete & restore: Admin-only
  - `DELETE /api/v1/events/{id}` → require `role=Admin`; marks soft-delete fields
  - `POST /api/v1/events/{id}/restore` → require `role=Admin`
  - `DELETE /api/v1/forms/{id}` → require `role=Admin`
  - `POST /api/v1/forms/{id}/restore` → require `role=Admin`

- Org scoping: All protected routes must scope by `org_id` claim
  - Use FastAPI dependency to resolve user/org and filter queries by `org_id`

## Audit & Logging
- Record actions: publish, archive/delete/restore, role changes, CSV exports, billing events
- Include actor, resource, timestamp, and request ID

## Email Verification & Password Reset (v0.2)
- Verification
  - Table: `EmailVerificationToken(user_id, token, expires_at, consumed_at)`
  - Flow: signup -> issue token -> email deep-link -> verify endpoint marks user as verified -> allow login to app areas
  - Resend: cooldown 60s and max 5 attempts/day (configurable)
- Password Reset
  - Table: `PasswordResetToken(user_id, token, expires_at, consumed_at)`
  - Flow: request reset -> email deep-link -> set new password -> invalidate all sessions
- Security
  - Tokens: random 32+ bytes, one-time use, short expiry (e.g., 30–60 min)
  - Rate limit endpoints; audit log token issuance/consumption

## Email Delivery
- Provider: SMTP by default; Postmark/SendGrid supported
- Templates: branded HTML for verification and reset; include expiry and support contact
- Bounces: monitor and flag addresses with repeated bounces; show UI prompt to correct email



