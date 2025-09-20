# Feature Flags — v2

Status: Active
Date: 2025-09-20

## Flags (names are canonical)
- flag:domain_claims — Enable Domain Claims email verification and UI
- flag:private_suggestions — Enable privacy-safe join hints
- flag:por_ledger — Enable PoR commission logic and ledger writes
- flag:entitlements — Enable SKU catalog and plan entitlements
- flag:metering — Enable metering ingest path
- flag:pricing_engine — Enable consumption pricing engine
- flag:budgets_caps — Enable budgets, caps, and alerts
- flag:validations — Enable validation add-ons (email/address/phone)
- flag:actions — Enable action services (email/SMS/docgen/webhook)
- flag:org_hierarchy — Enable org hierarchy and group roles
- flag:group_billing — Enable billing accounts and consolidated invoices
- flag:dashboard — Enable Head Office Dashboard and Assist Mode
- flag:estimator — Enable Builder Estimator panel

## Environment Variables
- FEATURE_DOMAIN_CLAIMS=true|false
- FEATURE_PRIVATE_SUGGESTIONS=true|false
- FEATURE_POR_LEDGER=true|false
- FEATURE_ENTITLEMENTS=true|false
- FEATURE_METERING=true|false
- FEATURE_PRICING_ENGINE=true|false
- FEATURE_BUDGETS_CAPS=true|false
- FEATURE_VALIDATIONS=true|false
- FEATURE_ACTIONS=true|false
- FEATURE_ORG_HIERARCHY=true|false
- FEATURE_GROUP_BILLING=true|false
- FEATURE_DASHBOARD=true|false
- FEATURE_ESTIMATOR=true|false

## Notes
- All flags default to false in production; enable progressively per environment.
- Combine with config for PoR real-time threshold (AUD 50) and rate limits.
