# ST-Validation-AddOns

Type: Story
Status: Pending
Epic: Consumption UX & Billing
Links.requires: ["ENA-Entitlements", "ENA-Metering-Service"]

## Description
Add email/address/phone checks with prepaid credits, rate limits, and error UX.

## Acceptance Criteria
1. Prepaid credits required for validations; UI warns when insufficient.
2. Rate limits enforced; user-facing error messages and retry hints.
3. Metering events emitted for validations; pricing applied accordingly.
