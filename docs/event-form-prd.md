> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Product Requirements Document: Visual Form Builder for Event Leads

## 1. Goals and Background Context

The goal is to build a visually rich, enterprise-ready platform that enables companies to design event lead capture forms using a drag-and-drop interface. The form builder is restricted to desktop environments due to its precision layout features, while the rest of the platform is responsive and usable on mobile for event management tasks like reviewing leads and invoices. The product will support multi-user companies with role-based access, billing and invoice functionality, and support for extensible field types.

## 2. Requirements

### Visual Form Builder (Desktop Only) - Primary Milestone

* Drag-and-drop interface with absolute positioning
* Canvas area for design, restricted to a 16:9 layout by default (e.g., 1920x1080)
* Custom canvas layouts per aspect ratio (landscape, portrait, mobile, desktop)
* Properties window for field customization (label, export label, tab order, required, default value, color, visibility, box styling)
* Support for drop-down fields with user-defined options and default selection
* Field ordering control for tab navigation
* Background image per form with zoom and placement control
* Option to set canvas background color if image is omitted
* Objects constrained to canvas boundaries
* Snapping to grid or automatic alignment of objects
* Design preview required before form can be finalized
* Preview of form layout for desktop, tablet, mobile
* Unique public URL generated per form; active during event duration
* Default layout fallback if no device-specific design exists

### Field Type Framework

* Extensible architecture for adding new field types in the future
* Control over which organizations see specific custom field types
* Company-specific field type configurations
* Each field type (e.g., TextField, DropdownField, CheckboxField) in its own table
* Shared `CanvasObject` base with `ObjectType` registry for polymorphic handling
* Form design stores object references linked to its canvas version

### User Roles and Permissions

* Multi-tenant (companies as tenants)
* First user = Company Admin
* Admins can invite others and assign roles (Admin, User)
* Only Admins can publish events (trigger billing)

### Billing and Invoicing

* Events remain in draft until published
* Payment required to go live (e.g. \$50 per day)
* Invoice generated with company info
* Events live for 24h + 3h buffer
* Multi-day = additional payments
* Tier-based limits (MaxUsers, MaxEvents)

### Mobile Functionality

* Responsive design for event list, lead review, invoices, user invites
* Form builder disabled on mobile

### Platform Features

* Landing page for marketing and login/signup
* Tenant-based isolated environments
* Event cloning and reusable designs
* Background images stored in `FormBuilderImage` table
* Form versioning with `RevisionNumber`

## 3. User Interface Design Goals

* Clean, modern UI
* Desktop-first form builder with WYSIWYG 16:9 canvas
* Canvas centered between left-side menu and right-side properties panel
* Zoom/placement control for background images
* Objects must contrast with background (color, borders, boxing)
* Mobile-first design for non-builder features
* Device previews in multiple resolutions
* Tabbed panels for field properties and layout management
* Grid snapping and auto-alignment
* Registry-driven editors for extensibility

## 4. Success Metrics

* Users onboard and create first event in <10 minutes
* > 80% of published events capture leads
* <5% churn after initial event creation
* Support tickets <1% of active users

## 5. Constraints & Dependencies

* Payment integration (Stripe)
* Multi-tenant security isolation
* Layout engine must render responsively
* Builder limited to desktop (no tablet/mobile editing)
* All objects/properties stored structurally in DB
* Registry-driven rendering for extensibility

## 6. Out of Scope (MVP)

* Analytics dashboards/reporting
* Custom branding/white-labeling
* Public API
* Complex conditional logic fields
* Protected Zones

## MVP Sequencing Notes (v0.2)

- Visual Builder MVP is delivered before public slug/public runtime.
- `Form.public_slug` is generated when a form is marked Ready/Published (post-builder), not at initial creation.
- Stripe billing is included in MVP for publish/usage charges and invoices.

---

*Document owned by PM Agent. UX and Architect validation required before locking.*
