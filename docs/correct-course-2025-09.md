# Correct Course — September 2025

Scope: Align MVP to user workflow, move Builder earlier, tie slug to publish, include Stripe in MVP, and codify RBAC and data-first standards.

Decisions
- Builder earlier than slug/public runtime; slug generated on Ready/Publish.
- Stripe included in MVP: publish flow, usage charges, webhooks, invoice rollup.
- Roles: Admin can change others’ roles, not their own; maintain ≥1 Admin per org.
- Data-first: All configuration/state persisted in DB; migrations with downgrade; indexes for dashboard.
- Global settings: add `GlobalSetting` with seed `invite_token_ttl_hours=48`.
- Invitations: secure token (≥32 bytes), 48h expiry; invitee sets password.
- Field types: registry + seeds (Text, Dropdown, Checkbox); org visibility toggles.

Roadmap (abbrev)
- M1: Global Settings + Onboarding + Invitations (Stories 0003–0004)
- M1.5: Dashboard Scaffold (0005)
- M2: Events & Forms (Draft) + CanvasLayout + Field Types (0006–0009)
- M3: Visual Builder MVP + Text/Dropdown/Checkbox (0010–0013)
- M4: Slug & Public Runtime (0014)
- M5: Publish & Stripe Billing (0015)

Shard refs: docs/shards/02-data-schema.md, docs/shards/04-auth-rbac.md, docs/shards/05-devops-migrations.md, docs/shards/03-billing-go-live.md
