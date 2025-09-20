# ST-Action-Services

Type: Story
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-Metering-Service"]

## Description
Implement email/SMS/doc-gen/webhook retries metered with quotas; provider abstraction with retries, DLQ, and audit.

## Acceptance Criteria
1. Provider adapters implement idempotent send with retry/backoff; DLQ on persistent failure.
2. Metering events emitted per action; budgets/caps enforced at initiation.
3. Audit and structured logs include request_id and redacted payloads.
4. Error UX: show status during retry; on DLQ, surface an admin-visible log entry and user copy: “This action couldn’t be delivered and requires attention. See Admin Logs.”
