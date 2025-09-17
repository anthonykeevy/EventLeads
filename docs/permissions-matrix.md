# Permissions Matrix

Defines role-based permissions for platform and organization resources.

## Roles
- SystemAdmin: Full platform administration across all organizations; manage global settings and overrides.
- Admin: Full administrative control over organization resources.
- User: Contributor with restricted edit/publish/billing rights.
- Public: Unauthenticated participant for production form submissions only.

## Resources & Actions

- Organization
  - SystemAdmin: view/manage all orgs; create/disable orgs; assign Admins
  - Admin: view, update org settings; invite/remove users; change roles
  - User: view

- Users & Invites
  - SystemAdmin: manage users and roles across orgs; force reset/disable
  - Admin: create invites, revoke, assign roles
  - User: accept invite; manage own profile

- Events
  - SystemAdmin: all Admin capabilities across orgs; override locks if needed (audited)
  - Admin: create, view, update, archive, delete, restore, publish controls
  - User: create, view all org events; update basic details; cannot archive/delete/restore; cannot publish

- Forms (per Event)
  - SystemAdmin: full control; can flip statuses with justification (audited)
  - Admin: create, view, update any; change status (Draft → ReadyForReview → ProductionEnabled)
  - User: create, view any; update only when status != ProductionEnabled; cannot enable production

- Canvas Layouts & Objects
  - SystemAdmin: full control
  - Admin: full control
  - User: full control only when parent Form status != ProductionEnabled

- Leads
  - SystemAdmin: view/export CSV across orgs; delete/restore (soft-delete)
  - Admin: view all; export CSV; delete/restore (soft-delete)
  - User: view all; no CSV export; cannot delete/restore
  - Public: submit production leads within event date window only

- Billing & Usage (Invoices, Entitlements/Usage)
  - SystemAdmin: view/override at platform level; recon tools; configure pricing keys
  - Admin: view invoices and usage; manage org billing settings
  - User: no access

- Settings
  - SystemAdmin: global platform settings (billing keys, SMTP/provider, feature flags)
  - Admin: configure Stripe/email/env-related app settings for their org
  - User: view-only where safe (optional)

## Access Scope
- Users can view all events in the organization.
- Users can edit/add Events and Forms, but only edit Forms that are not ProductionEnabled.
- SystemAdmin operates across all organizations and inherits Admin rights everywhere.

## Enforcement
- JWT claims: `role` in {SystemAdmin, Admin, User}; route guards enforce actions by role.
- UI hides or disables disallowed actions and shows clear messaging.
- Audit log: record publish, archive/delete/restore, role changes, CSV exports, billing actions.
- SystemAdmin overrides are allowed but must be audited with actor and justification.

## Acceptance Criteria
- Attempts to publish, export CSV, or modify ProductionEnabled forms as User are blocked with 403 and UX explanation.
- CSV export control visible to Admins only.
- Edit controls disabled on ProductionEnabled forms for Users; tooltip explains restriction.
