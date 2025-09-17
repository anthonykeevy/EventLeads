# Audit Logging

Purpose: Persist user-facing interaction events with explicit status for troubleshooting and customer visibility (Admin), starting with authentication flows.

## Scope (MVP)
- Auth interactions: signup, verification, resend, login, logout, reset-request, reset-confirm
- Record attempt/success/failure with reason codes
- Expose Admin query API scoped to their organization

## Event Taxonomy (Auth)
- signup_attempt, signup_success, signup_failure
- verification_attempt, verification_success, verification_failure
- resend_attempt, resend_success, resend_limited (429)
- login_attempt, login_success, login_failure (invalid_credentials | unverified | locked)
- logout
- reset_request_attempt, reset_request_success
- reset_confirm_attempt, reset_confirm_success, reset_confirm_failure (invalid | expired)

## Event Schema (AuthEvent)
- `AuthEventID` bigint identity PK
- `OrganizationID` int NULL (nullable for pre-org signup)
- `UserID` int NULL
- `Email` nvarchar(256) NULL (as provided)
- `EventType` nvarchar(64) NOT NULL (see taxonomy)
- `Status` nvarchar(16) NOT NULL (attempt | success | failure)
- `ReasonCode` nvarchar(64) NULL (e.g., invalid_credentials, unverified, expired)
- `RequestID` nvarchar(64) NULL (correlates to logs/traces)
- `IP` nvarchar(64) NULL
- `UserAgent` nvarchar(256) NULL
- `CreatedDate` datetime2 NOT NULL DEFAULT GETUTCDATE()

Notes
- Do NOT store passwords or tokens.
- Emails may be stored for correlation; honor deletion/erasure requests by pseudonymizing if required later.

## API (Admin)
- `GET /api/v1/audit/auth?from=&to=&email=&event=&status=&reason=&user_id=`
  - Scope: Admin/SystemAdmin only; Admin limited to their org
  - Pagination required

## UI (Admin)
- Organization Settings → Audit → Authentication
  - Filters: date range, event type, status, email, reason
  - Columns: time, event, status, reason, email, IP, user agent, request ID

## Retention
- Default: 90 days (configurable)
- Export: Admin CSV export available (audit trail), subject to RBAC

## Observability Bridging
- Each AuthEvent should include `RequestID` so Admin audit rows can align with server logs and traces.
