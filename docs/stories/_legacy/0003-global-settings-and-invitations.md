> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0003 — Global Settings & Invitations (48h TTL)

Status: Completed (UAT Accepted)
Epic: M1 — Onboarding, Invitations, Global Settings
Owners: Backend, Frontend, DevOps

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/05-devops-migrations.md#alembic-flow
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples

## Context
Introduce a `GlobalSetting` table to persist enterprise-wide configuration (e.g., invitation TTL) and implement organization-scoped Invitations with secure acceptance. Admins can invite users; invitees set their own password on acceptance. Admins cannot change their own role (no self-demote).

## Requirements
- `GlobalSetting(key, value, value_type, scope, created_at, updated_at)` with seed: `invite_token_ttl_hours = 48`.
- Invitations: `Invitation(id, org_id, email, role, token, expires_at, consumed_at, created_by, created_at)`.
- Secure accept flow: invite link with one-time token (≥32 bytes), expires per GlobalSetting; invitee sets password.
- Rate limit invite creation/resend; audit issuance and acceptance.

## Acceptance Criteria
1) Create GlobalSetting and seed `invite_token_ttl_hours = 48` (upgrade) with rollback (downgrade).
2) Admin can create an invite for an email and role; response 201 with redacted info (never return token).
3) System emails invite link (dev: log to console or MailHog) with one-time token; rate-limited with retry-after headers.
4) Accept invite: given valid, unconsumed, unexpired token → user sets password and joins org with specified role; token consumed; audit written.
5) Admin cannot change their own role; at least one Admin must always exist per org.

## API (initial)
- POST /api/v1/invitations {email, role}
- POST /api/v1/invitations/{token}/accept {password}
- GET  /api/v1/settings (Admin/SystemAdmin)

## Data & Config
- All booleans stored as BIT per standards; indexes on `Invitation(org_id, email, created_at)`.
- Settings service reads from `GlobalSetting` with in-process memoization and cache invalidation TTL.

## Definition of Done
- Alembic migration with upgrade/downgrade and seed; tests for token expiry and acceptance.
- Endpoints protected per RBAC; rate limits enforced; audited events persisted.
- Docs updated; shard citations present in PR.

## Verification
- Dev SQL Server: `GlobalSetting` table present; seed rows: `invite_token_ttl_hours=48`, `invite_daily_limit=100`.
- Evidence: `docs/story-0003-implementation-walkthrough.md` (QA + UAT), `devtools/story-0003/*` scripts.

## Scope Changes & UAT Enhancements (added during implementation)
- GlobalSetting seed extended: `invite_daily_limit` with idempotent migration; app reads via settings service
- Invitations email: British English copy; styled HTML; TTL injected from settings; inviter display name
- Frontend Accept page: personalised copy via new `GET /invitations/{token}/preview`; client-side validation (length, mismatch)
- Success UX: short success pause → redirect to `/login?email=...` with prefilled email
- Frontend routing: automatic proxy rewrites to backend so UAT works without env tweaks
- Backend Accept: marks `EmailVerified=1` and `IsActive=1` for both new and existing users; sets password for existing users
- Invitation create: first_name/last_name now required; user is pre-created and attached to the organisation to skip onboarding

## Original Scope vs Completed
- Original: settings seed (TTL), basic invite create/accept, rate limiting, audit, MailHog email
- Completed: all original items plus UI/UX improvements (HTML emails, British English), settings-driven rate limit, personalised Accept page, login handoff with email prefill, required names and pre-created users, and idempotent seeding for future environments