# Story 0003 — Implementation Walkthrough

Scope: GlobalSetting table + seed for invitation TTL (48h) and initial retrieval usage.

Changes
- Alembic migration `a015_globalsetting_table` creates `GlobalSetting` and seeds `invite_token_ttl_hours=48`.
- Columns: GlobalSettingID (PK), Key (unique), Value, ValueType, Scope (default 'global').

Verification
- Apply migration: `alembic upgrade head` (SQLite/SQL Server)
- Check row: `SELECT * FROM GlobalSetting WHERE Key='invite_token_ttl_hours'` → Value='48'
- Downgrade: `alembic downgrade -1` removes table and seed (best‑effort row delete first)

Usage (initial)
- Access settings via simple query in services (cache layer to follow in next task):

```python
from sqlalchemy import select, text
from backend.app.core.db import SessionLocal

with SessionLocal() as session:
    ttl_row = session.execute(
        text("SELECT Value FROM GlobalSetting WHERE [Key] = :k"),
        {"k": "invite_token_ttl_hours"},
    ).first()
    invite_ttl_hours = int(ttl_row[0]) if ttl_row and ttl_row[0] is not None else 48
```

Settings Service (added)
- File: `backend/app/services/settings_service.py` provides TTL-cached accessors, including `get_invite_token_ttl_hours()` and `get_invite_daily_limit()`.

Invitation Migration (added)
- File: `backend/migrations/versions/a016_invitation_table.py` creates `Invitation` with indexes `IX_Invitation_Org_CreatedAt` and `IX_Invitation_Email`.
- Seed: `a017_seed_invite_daily_limit` inserts `invite_daily_limit` idempotently.
- Evidence (Dev SQL Server): `{'exists': True, 'sample': []}` via `devtools/story-0003/verify_invitation.py`.

Invitation Endpoints (added)
- File: `backend/app/routers/invitations.py` implements:
  - POST `/api/v1/invitations` (Admin-only, rate-limited from GlobalSetting, redacted response)
  - POST `/api/v1/invitations/{token}/accept` (validate/consume token, set password, assign role/org)
- Evidence (Dev run):
  - QA script `devtools/story-0003/qa_invitations_test.py` output:
    - `{ 'create_status': 201, 'accept_status': 200, 'email': 'qa_user_<ts>@example.com' }`
    - Mail log: `[EMAIL][SUCCESS] Email sent successfully via SMTP`
  - Negative cases `devtools/story-0003/qa_invitations_negative_tests.py`:
    - `{ 'expired_status': 410, 'consumed_status': 410, 'invalid_status': 404, 'rate_limit_status': 429, 'retry_after': '3600' }`
  - Email template: British English copy (“organisation”), friendly HTML and plain text; preview via `devtools/story-0003/send_invite_preview.py`.

Shard citations: docs/shards/02-data-schema.md, docs/shards/05-devops-migrations.md, docs/shards/04-auth-rbac.md

## QA Results
- SQLite: upgrade/downgrade pass; seed exists with Value='48'.
- SQL Server: upgrade/downgrade pass; seed exists with Value='48' and `invite_daily_limit='10'`.
- Service check: `settings_service.get_invite_token_ttl_hours()` returns 48; `get_invite_daily_limit()` returns 10.
- Invitation: table exists on Dev; indexes present (verified via metadata).
- Endpoints:
  - Create: 201, redacted body; admin auth; email logged to MailHog.
  - Accept: 200; token consumed.
  - Negative: expired 410, consumed 410, invalid 404; rate limit 429 with `Retry-After: 3600`.
- Logs clean; no secrets leaked; shard citations present in PR description.

## UAT Results
- PO verified email copy (British English), seeded settings, and end-to-end invite/accept flows on Dev. UAT PASSED.

## Handover
Next Agent: Frontend (Dev)
Notes: Implement Accept Invitation page at `/invite/accept` (extract token, password form, call POST `/api/v1/invitations/{token}/accept`, British English copy, success/error states).

## v2 Acceptance Criteria Updates (2025-09-20)

Scope: Invitations and settings align with org-scoped model and DomainClaims, with privacy and caps.

- Invitations are org-scoped and unique per `(org_id, lower(email))` until consumed; duplicates in pending state rejected with 409.
- TTL sourced from `GlobalSetting.invite_token_ttl_hours`; daily cap from `invite_daily_limit`; on cap reached, respond 429 and set `Retry-After`.
- Accept flow validates token, enforces password policy, consumes token, creates membership in correct org, and audits actor/target.
- DomainClaims interaction: if invite email domain matches a verified `domain_claim` for the org, UI shows reduced friction; if not, normal flow. No identity leakage in any case.
- Privacy-safe join routing from PRD v2: signups that match verified domains are prompted to Request to Join rather than creating duplicate orgs.
- Telemetry: `invite_create`, `invite_accept`, `invite_rate_limited` emitted with request_id correlation.
- Frontend: implement `/invite/accept` page with success/error states, British English copy, and accessibility per spec.

Cross-links: `docs/prd/v2-prd.md` (Privacy & Discovery; Domain Claims), `docs/architecture/v2-architecture.md` (Tenancy & Domain Claims), ADR‑002, ADR‑003, ADR‑004, ADR‑005, dashboard ACs in `docs/front-end-spec/head-office-dashboard.md`.

Shard refs: `docs/shards/02-data-schema.md`, `docs/shards/04-auth-rbac.md`