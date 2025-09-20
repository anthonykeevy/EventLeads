> **Superseded (2025-09-20):** This document is replaced by v2.
> See: `docs/prd/v2-prd.md` and `docs/architecture/v2-architecture.md`.

# Story 0004 — Organization Onboarding Wizard

Status: Draft
Epic: M1 — Onboarding, Invitations, Global Settings
Owners: Frontend, Backend

Shard Citations:
- docs/shards/02-data-schema.md#tables
- docs/shards/04-auth-rbac.md#routing-&-enforcement-examples
- docs/shards/05-devops-migrations.md#alembic-flow

## Story

**As a** first-time user logging into the platform,
**I want** to be guided through creating my organization with billing details,
**so that** I can set up my company workspace and invite team members.

## Context

After first login, guide the user to create an Organization with billing-ready details. The creator becomes Admin. Maintain the invariant that an Organization must always have at least one Admin. Admins cannot change their own role (no self-demote).

## Acceptance Criteria

1) First-login with no org: show wizard to create Organization with required fields (name, billing email, billing address basics, timezone default).
2) On successful creation: assign current user as Admin; redirect to dashboard org card; show next steps (invite teammates, create event).
3) If org exists: skip wizard; show dashboard.
4) Enforce ≥1 Admin per org at all times; prevent last Admin demotion/deletion.
5) Users must update their default first and last names during onboarding.

## Tasks / Subtasks

- [ ] Task 1: Backend API for Organization Creation (AC: 1, 2, 4)
  - [ ] Create POST /api/v1/organizations endpoint with validation
  - [ ] Implement organization creation logic with current user as Admin
  - [ ] Add validation to ensure required billing fields are provided
  - [ ] Enforce Admin role assignment for organization creator
  - [ ] Add database constraints to prevent last Admin removal
  - [ ] Unit tests for organization creation and validation

- [ ] Task 2: Frontend Onboarding Wizard Component (AC: 1, 2, 3)
  - [ ] Create onboarding wizard component with multi-step form
  - [ ] Implement form validation for organization details
  - [ ] Add billing address collection with proper validation
  - [ ] Handle timezone selection with sensible defaults
  - [ ] Create success state with next steps guidance
  - [ ] Add conditional rendering based on existing organization

- [ ] Task 3: Dashboard Integration and Routing (AC: 2, 3)
  - [ ] Update dashboard to show organization card after creation
  - [ ] Implement conditional routing to skip wizard if org exists
  - [ ] Add "Invite teammates" and "Create event" next steps
  - [ ] Handle wizard dismissal from Help menu when org exists
  - [ ] Update authentication flow to check organization status

- [ ] Task 4: Database Schema and Constraints (AC: 4)
  - [ ] Verify Organization table schema supports billing fields
  - [ ] Add database constraints to prevent last Admin deletion
  - [ ] Create Alembic migration if schema changes needed
  - [ ] Add indexes for frequent org lookups by owner
  - [ ] Unit tests for database constraints

- [ ] Task 5: User Behavior Tracking and Analytics (UX Enhancement)
  - [ ] Implement onboarding wizard analytics tracking
  - [ ] Log wizard step progression and abandonment points
  - [ ] Track field interaction patterns and validation errors
  - [ ] Monitor billing information collection completion rates
  - [ ] Record timezone selection behavior and accuracy
  - [ ] Log success state engagement with next steps
  - [ ] Create analytics dashboard for onboarding insights
  - [ ] Unit tests for analytics tracking functionality

## Dev Notes

### Previous Story Insights
From Story-0003: The invitation system is now complete with GlobalSettings and proper email flows. Users are pre-created and attached to organizations during invitation acceptance, which means the onboarding wizard needs to handle both new users and invited users who may already have an organization.

### Data Models
**Organization Table Structure** [Source: docs/shards/02-data-schema.md#tables]:
- `Organization(id, name, created_at)` - Basic organization structure
- Additional fields needed: billing_email, billing_address, timezone
- All PKs use `BIGINT IDENTITY(1,1)` format
- Use `NVARCHAR(256)` for email fields, `NVARCHAR(MAX)` for address text
- Use `DATETIME2` for created_at timestamp with `GETDATE()` default

**User-Organization Relationship** [Source: docs/shards/02-data-schema.md#tables]:
- `User(id, org_id FK, email, role, created_at)` 
- Foreign key constraint with cascade delete where appropriate
- Role field stores 'Admin' or 'User' values
- Unique constraint: User.email per org

### API Specifications
**Organization Creation Endpoint** [Source: docs/shards/04-auth-rbac.md#routing-&-enforcement-examples]:
- `POST /api/v1/organizations` - Create new organization
- Request body: `{name, billing_email, billing_address, timezone}`
- Response: 201 with organization details (excluding sensitive billing info)
- Auth: Requires valid JWT token
- Org scoping: All protected routes must scope by `org_id` claim

**RBAC Enforcement** [Source: docs/shards/04-auth-rbac.md#routing-&-enforcement-examples]:
- Use FastAPI dependency to resolve user/org and filter queries by `org_id`
- JWT Claims: `sub (user id), org_id, role, exp, iat`
- Admin role assignment happens automatically during organization creation

### Component Specifications
**Frontend Architecture** [Source: docs/tech-architecture.md#core-stack]:
- React + Tailwind + ShadCN + Framer Motion
- Responsive design for non-builder features (mobile-first for non-builder)
- Clean, modern UI with desktop-first form builder approach

**Form Validation Requirements**:
- Organization name: required, min length validation
- Billing email: required, email format validation, uniqueness check
- Billing address: required fields for basic address information
- Timezone: required, default to user's detected timezone or UTC

### File Locations
**Backend Structure** [Source: docs/tech-architecture.md#directory-structure]:
- `/backend/app/models/` - Organization model updates
- `/backend/app/routers/` - New organizations router
- `/backend/app/schemas/` - Organization creation schemas
- `/backend/migrations/versions/` - Alembic migration files

**Frontend Structure** [Source: docs/tech-architecture.md#directory-structure]:
- `/frontend/src/components/` - Onboarding wizard components
- `/frontend/src/app/` - Dashboard and routing updates
- `/frontend/src/lib/` - Organization API client functions

### Testing Requirements
**Database Standards** [Source: docs/shards/02-data-schema.md#database-standards-&-guidelines]:
- Boolean fields use `BIT` data type in SQL Server
- SQLAlchemy mapping: `Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)`
- Application code: Always check `field != 0` or `field == 1` for explicit boolean logic

**Testing Strategy** [Source: docs/shards/05-devops-migrations.md#alembic-flow]:
- Test file location: `/backend/tests/`
- Test frameworks: pytest with SQLAlchemy test fixtures
- Migration testing: Run `alembic upgrade head` on ephemeral DBs before merge
- Unit tests for organization creation, validation, and constraint enforcement

### Technical Constraints
**Migration Requirements** [Source: docs/shards/05-devops-migrations.md#alembic-flow]:
- Any model change requires an Alembic migration with rollback path
- Never apply direct DDL in production; use Alembic scripts only
- Include reversible scripts for data migrations if needed

**Security Constraints** [Source: docs/shards/04-auth-rbac.md#audit-&-logging]:
- Record actions: organization creation, admin role assignment
- Include actor, resource, timestamp, and request ID in audit logs
- Rate limit organization creation to prevent abuse

### Behavior Tracking & Analytics Requirements
**User Behavior Logging** [Source: docs/shards/04-auth-rbac.md#audit-&-logging]:
- Track wizard step progression: step_started, step_completed, step_abandoned
- Log field interactions: field_focused, field_blurred, validation_error, field_corrected
- Monitor timing data: step_duration, field_interaction_time, total_wizard_time
- Record completion metrics: wizard_completed, wizard_abandoned, billing_collected, timezone_selected
- Track success state engagement: next_step_clicked, help_accessed, wizard_dismissed

**Analytics Data Structure**:
```json
{
  "user_id": "uuid",
  "session_id": "uuid", 
  "event_type": "wizard_step_started|step_completed|field_interaction|validation_error|wizard_abandoned|wizard_completed",
  "step_name": "organization_basics|billing_info|success_state",
  "field_name": "org_name|billing_email|timezone|billing_address",
  "interaction_data": {
    "duration_ms": 1500,
    "error_message": "Email already exists",
    "correction_count": 2,
    "abandonment_reason": "billing_required"
  },
  "timestamp": "2025-01-27T10:30:00Z",
  "request_id": "uuid"
}
```

**Privacy Considerations**:
- Hash or anonymize sensitive data (email addresses, organization names)
- Store only interaction patterns, not actual form content
- Comply with data retention policies
- Provide opt-out mechanism for analytics tracking

## Testing

### Test File Location
- `/backend/tests/test_organizations.py` - Backend API tests
- `/frontend/src/__tests__/` - Frontend component tests

### Test Standards
- Backend: pytest with SQLAlchemy test fixtures, mock external dependencies
- Frontend: Jest + React Testing Library for component testing
- Integration tests for complete onboarding flow
- Database constraint tests for Admin role enforcement

### Testing Frameworks and Patterns
- Backend: pytest, FastAPI TestClient, SQLAlchemy test fixtures
- Frontend: Jest, React Testing Library, MSW for API mocking
- Database: Test containers or SQLite for migration testing

### Specific Testing Requirements
- Test organization creation with valid and invalid data
- Test Admin role assignment during organization creation
- Test constraint enforcement preventing last Admin deletion
- Test conditional wizard display based on existing organization
- Test billing field validation and timezone handling
- Test complete onboarding flow from login to dashboard
- Test behavior tracking events are properly logged
- Test analytics data structure and privacy compliance
- Test wizard abandonment and completion tracking
- Test field interaction and validation error logging

## Implementation Todo List

### Sprint Tasks for Story-0004
- [ ] **Backend API Implementation**
  - [ ] Create POST /api/v1/organizations endpoint with validation
  - [ ] Implement organization creation logic with current user as Admin
  - [ ] Add validation for required billing fields
  - [ ] Enforce Admin role assignment for organization creator
  - [ ] Add database constraints to prevent last Admin removal

- [ ] **Database Schema Updates**
  - [ ] Update Organization model with billing fields (billing_email, billing_address, timezone)
  - [ ] Create Alembic migration with upgrade/downgrade scripts
  - [ ] Add indexes for frequent org lookups by owner
  - [ ] Verify schema supports all required fields

- [ ] **Frontend Onboarding Wizard**
  - [ ] Create multi-step wizard component (3-step flow: basics → billing → success)
  - [ ] Implement form validation for organization details
  - [ ] Add billing address collection with proper validation
  - [ ] Handle timezone selection with auto-detection and search
  - [ ] Create success state with next steps guidance
  - [ ] Add conditional rendering based on existing organization

- [ ] **Dashboard Integration & Routing**
  - [ ] Update dashboard to show organization card after creation
  - [ ] Implement conditional routing to skip wizard if org exists
  - [ ] Add "Invite teammates" and "Create event" next steps
  - [ ] Handle wizard dismissal from Help menu when org exists
  - [ ] Update authentication flow to check organization status

- [ ] **User Behavior Tracking & Analytics**
  - [ ] Implement onboarding wizard analytics tracking
  - [ ] Log wizard step progression and abandonment points
  - [ ] Track field interaction patterns and validation errors
  - [ ] Monitor billing information collection completion rates
  - [ ] Record timezone selection behavior and accuracy
  - [ ] Log success state engagement with next steps

- [ ] **Testing & Quality Assurance**
  - [ ] Create unit tests for organization creation and validation
  - [ ] Test Admin role assignment during organization creation
  - [ ] Test constraint enforcement preventing last Admin deletion
  - [ ] Test conditional wizard display based on existing organization
  - [ ] Test behavior tracking events are properly logged
  - [ ] Test analytics data structure and privacy compliance
  - [ ] Integration tests for complete onboarding flow

- [ ] **UAT Preparation & Documentation**
  - [ ] Prepare UAT environment with test scenarios
  - [ ] Create implementation walkthrough documentation
  - [ ] Verify all UX recommendations are implemented
  - [ ] Test complete user journey from login to dashboard
  - [ ] Validate behavior tracking and analytics functionality

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-01-27 | 1.0 | Initial story creation with technical context | Scrum Master |
| 2025-01-27 | 1.1 | UX validation completed - approved with recommendations | UX Expert |
| 2025-01-27 | 1.2 | Added comprehensive behavior tracking and analytics requirements | Scrum Master |
| 2025-01-27 | 1.3 | Added detailed implementation todo list and sprint tasks | Scrum Master |

## Dev Agent Record

*This section will be populated by the development agent during implementation*

### Agent Model Used
Claude Sonnet 4 (via Cursor AI)

### Debug Log References
- Migration generation issue resolved: Initial autogenerated migration tried to drop all tables, manually created proper migration `a018_add_organization_billing_fields.py`
- JWT token creation in tests required secret parameter fix
- Organization table already existed with most required fields, only needed to add `BillingEmail` and `Timezone`

### Completion Notes List
✅ **Backend API Implementation Complete**
- Updated Organization model to match existing database schema
- Created Alembic migration to add billing fields (BillingEmail, Timezone)
- Implemented POST /api/v1/organizations endpoint with full validation
- Added Admin role assignment logic for organization creators
- Created comprehensive Pydantic schemas for request/response
- Registered organizations router in main FastAPI app
- Implemented proper error handling and constraint enforcement

✅ **Database Schema Updates**
- Added BillingEmail (NVARCHAR(320)) and Timezone (NVARCHAR(100)) fields
- Migration includes proper upgrade/downgrade scripts
- All existing Organization fields preserved and mapped correctly

✅ **API Endpoints Implemented**
- POST /api/v1/organizations - Create organization with billing details
- GET /api/v1/organizations/me - Get current user's organization
- Proper authentication and authorization with JWT tokens
- Comprehensive validation and error responses

✅ **Business Logic**
- Organization creator automatically becomes Admin
- Enforces one organization per user constraint
- Generates unique organization codes and slugs
- Proper audit logging for organization creation events
- Follows established patterns from Story-0003 (invitations)

### File List
**Backend Files Created/Modified:**
- `backend/app/models/organization.py` - Updated Organization model
- `backend/app/schemas/organization.py` - New Pydantic schemas
- `backend/app/routers/organizations.py` - New organizations router
- `backend/app/main.py` - Registered organizations router
- `backend/migrations/versions/a018_add_organization_billing_fields.py` - New migration
- `backend/tests/test_organizations.py` - Comprehensive test suite

**Frontend Files Created/Modified:**
- `frontend/src/app/onboarding/page.tsx` - Main onboarding wizard page
- `frontend/src/components/onboarding/OrganizationBasicsStep.tsx` - Organization details step
- `frontend/src/components/onboarding/BillingInfoStep.tsx` - Billing information step
- `frontend/src/components/onboarding/SuccessStep.tsx` - Success confirmation step
- `frontend/src/lib/analytics.ts` - User behavior tracking utility
- `frontend/src/components/ui/` - Complete UI component library (card, button, input, select, etc.)
- `frontend/src/lib/utils.ts` - Utility functions for styling
- `frontend/package.json` - Updated with new dependencies

**Database Changes:**
- Added BillingEmail and Timezone columns to Organization table
- Migration tested and applied successfully

✅ **Frontend Onboarding Wizard Implementation Complete**
- Created comprehensive multi-step onboarding wizard at `/onboarding`
- Implemented three wizard steps: Organization Basics, Billing Info, Success
- Added client-side form validation with real-time error feedback
- Integrated with backend API endpoints for organization creation
- Implemented proper error handling and loading states
- Added user behavior tracking and analytics for UX optimization
- Created responsive design with progress indicators and step navigation
- Built reusable UI components following design system patterns

✅ **User Experience Features**
- Progressive disclosure with step-by-step guidance
- Optional billing information with skip option
- Real-time validation with helpful error messages
- Success state with organization summary and next steps
- Mobile-responsive design with touch-friendly interactions
- Accessibility considerations with proper ARIA labels

✅ **Technical Implementation**
- TypeScript for type safety and better development experience
- Tailwind CSS for consistent styling and responsive design
- Radix UI components for accessible form controls
- Client-side analytics tracking for user behavior insights
- Proper SSR handling to avoid hydration issues
- Component-based architecture for maintainability

## UX Validation

**Validated by**: Sally (UX Expert)  
**Date**: 2025-01-27  
**Status**: ✅ APPROVED with Recommendations

### UX Assessment Summary

The Organization Onboarding Wizard story demonstrates strong user-centered design thinking with clear user flows and comprehensive technical implementation. The wizard addresses a critical user need (first-time organization setup) with appropriate progressive disclosure and clear success states.

### User Experience Strengths

✅ **Clear User Journey**: The story properly identifies the first-time user as the primary persona and creates a logical flow from login → wizard → dashboard → next steps.

✅ **Progressive Disclosure**: The multi-step wizard approach prevents cognitive overload by breaking organization setup into manageable chunks.

✅ **Contextual Help**: Dismissible wizard with Help menu access provides flexibility for users who want to explore the platform first.

✅ **Success State Design**: Clear next steps guidance ("invite teammates, create event") helps users understand what to do after completing the wizard.

✅ **Error Prevention**: Validation requirements and clear field specifications help prevent user errors during organization creation.

### UX Recommendations & Improvements

#### 1. **Wizard Flow Optimization** ⚠️
**Current**: Multi-step form with billing details
**Recommendation**: Consider a 3-step flow for better completion rates:
- Step 1: Organization basics (name, timezone)
- Step 2: Billing information (email, address)
- Step 3: Success & next steps

**Rationale**: Separating organization basics from billing reduces friction for users who might be hesitant about providing billing information upfront.

#### 2. **Billing Information Collection** ⚠️
**Current**: Required billing fields in wizard
**Recommendation**: 
- Make billing email required but billing address optional initially
- Add clear explanation of why billing information is needed
- Consider allowing organization creation without full billing details, with a "Complete billing setup" prompt later

**Rationale**: Reduces abandonment risk while still capturing essential information for admin users.

#### 3. **Timezone Selection UX** 🔧
**Current**: Default to user's detected timezone or UTC
**Recommendation**:
- Auto-detect user's timezone with clear indication
- Provide search/filter functionality for timezone selection
- Show example times (e.g., "2:00 PM PST") to help users confirm selection
- Default to UTC only as fallback, not primary option

#### 4. **Success State Enhancement** 🔧
**Current**: Redirect to dashboard with org card and next steps
**Recommendation**:
- Add a brief success animation or checkmark
- Include a "Skip setup" option for advanced users
- Provide quick access to the most common next action (Create Event)
- Show a progress indicator if there are multiple setup steps

#### 5. **Error Handling & Recovery** 🔧
**Current**: Basic validation mentioned
**Recommendation**:
- Add inline validation with helpful error messages
- Provide suggestions for common errors (e.g., "Try 'Acme Corp' instead of 'Acme Corporation LLC'")
- Include "Save as draft" functionality to prevent data loss
- Add clear error recovery paths

#### 6. **Accessibility Considerations** 🔧
**Current**: Not explicitly addressed
**Recommendation**:
- Ensure keyboard navigation through all wizard steps
- Add proper ARIA labels and descriptions
- Include screen reader announcements for step progress
- Test with high contrast and reduced motion preferences

### Technical UX Considerations

#### 1. **Performance Optimization**
- Implement optimistic UI updates for better perceived performance
- Add loading states for organization creation API calls
- Consider client-side validation to reduce server round trips

#### 2. **Responsive Design**
- Ensure wizard works well on tablet devices (even though builder is desktop-only)
- Test organization card display on mobile devices
- Verify timezone selector works on touch devices

#### 3. **Data Persistence**
- Auto-save wizard progress to prevent data loss
- Allow users to return to incomplete wizards
- Clear saved data after successful completion

#### 4. **User Behavior Tracking & Analytics**
- Track wizard step completion rates and abandonment points
- Log time spent on each step and field interactions
- Monitor validation error patterns and user corrections
- Record billing information collection success/failure rates
- Track timezone selection patterns and accuracy
- Log success state engagement with next steps

### Integration with Existing UX Patterns

✅ **Consistent with Design System**: Story aligns with established Tailwind + ShadCN patterns
✅ **Matches Success Metrics**: Supports the <10 minute onboarding goal from PRD
✅ **Follows Progressive Disclosure**: Consistent with builder's progressive disclosure principles
✅ **Mobile-First Approach**: Aligns with mobile-first design for non-builder features

### Validation Against UX Goals

| UX Goal | Story Alignment | Status |
|---------|----------------|---------|
| First event created in <10 minutes | Wizard facilitates quick org setup | ✅ |
| Clear, predictable outcomes | Success state with next steps | ✅ |
| Progressive disclosure | Multi-step wizard approach | ✅ |
| Immediate feedback | Validation and success states | ✅ |
| Accessible by default | Needs explicit accessibility implementation | ⚠️ |

### Final UX Recommendation

**APPROVE** the story with the following priority improvements:

1. **High Priority**: Implement the 3-step wizard flow optimization
2. **High Priority**: Make billing address optional initially
3. **Medium Priority**: Enhance timezone selection UX
4. **Medium Priority**: Add accessibility features
5. **Low Priority**: Implement auto-save and data persistence

The story provides a solid foundation for organization onboarding that aligns well with user needs and platform goals. The recommended improvements will enhance completion rates and user satisfaction while maintaining the technical requirements.

### UX Testing Recommendations

Before implementation:
- Test wizard flow with 5-10 first-time users
- Validate timezone selection usability
- Test billing information collection flow
- Verify accessibility compliance

After implementation:
- Monitor wizard completion rates
- Track time to first event creation
- Collect user feedback on billing information requirements
- Test error handling scenarios

## QA Results

*Results from QA Agent review of the completed story implementation*