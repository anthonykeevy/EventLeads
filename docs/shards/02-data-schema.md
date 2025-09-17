# Data Schema

Source refs: ../event-form-prd.md, ../tech-architecture.md

## Database Standards & Guidelines

### Data Types & Field Standards

**Boolean Fields:**
- Use `BIT` data type for all boolean fields in SQL Server
- SQLAlchemy mapping: `Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)`
- Application code: Always check `field != 0` or `field == 1` for explicit boolean logic
- **NEVER** use `INT` for boolean values - this causes data type mismatches

**Common Boolean Fields:**
- `EmailVerified` - User email verification status
- `IsActive` - Entity active/inactive status  
- `IsDeleted` - Soft delete flag
- `IsTest` - Test data flag
- `Required` - Field requirement flag

**String Fields:**
- Use `NVARCHAR(MAX)` for variable-length text
- Use `NVARCHAR(n)` for fixed-length requirements (e.g., email: 256, role: 50)
- Always specify length constraints

**Numeric Fields:**
- Use `BIGINT IDENTITY(1,1)` for primary keys
- Use `INT` for foreign keys and small integers
- Use `DECIMAL(10,2)` for currency amounts

**Date/Time Fields:**
- Use `DATETIME2` for all timestamp fields
- Default to `GETDATE()` for created timestamps
- Use `GETUTCDATE()` only when timezone consistency is critical

### Code Standards

**SQLAlchemy Model Definition:**
```python
class User(Base):
    __tablename__ = "User"
    
    id: Mapped[int] = mapped_column("UserID", BigInteger, primary_key=True, autoincrement=True)
    email_verified: Mapped[bool] = mapped_column("EmailVerified", Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column("IsActive", Boolean, nullable=False, default=True)
```

**Application Logic:**
```python
# CORRECT: Explicit boolean checks
if user.get("EmailVerified") and user.get("EmailVerified") != 0:
    # User is verified

# INCORRECT: Implicit boolean conversion
if user.get("EmailVerified"):  # Can fail with integer 0/1
    # User is verified
```

**Database Queries:**
```sql
-- CORRECT: Explicit bit field usage
SELECT * FROM [User] WHERE EmailVerified = 1

-- CORRECT: Boolean logic
UPDATE [User] SET EmailVerified = 1 WHERE UserID = @user_id
```

Tables (min fields; see models for full definitions)
- Organization(id, name, created_at)
- User(id, org_id FK, email, role, created_at)
- Event(id, org_id FK, name, status, start_date, end_date, timezone, created_at, soft-delete)
- Form(id, event_id FK, name, status[Draft|ReadyForReview|ProductionEnabled], public_slug UNIQUE, soft-delete)
- CanvasLayout(id, form_id FK, device_type, aspect_ratio, resolution_x, resolution_y, revision_number, soft-delete)
- CanvasObject(id, layout_id FK, kind, x, y, w, h, z, created_at, soft-delete)
- TextField(id, layout_id FK, key, label, required, created_at)
- DropdownField(id, layout_id FK, key, label, options JSON, required, created_at)
- Lead(id, event_id FK, form_id FK, is_test, payload JSON, created_at, soft-delete)
- Invoice(id, org_id FK, amount_cents, status, created_at, soft-delete)
- EventDayEntitlement(id, org_id FK, event_id FK, date, amount_cents, invoice_id NULL)

Constraints
- All PKs: bigint identity; FK on delete cascade where appropriate
- Unique: User.email per org; Field.key per layout; Form.public_slug global unique; EventDayEntitlement unique (event_id, date)

Versioning Model
- Layouts and fields immutable once published; new versions via duplicate + increment
- CanvasLayout ties to a Form revision; publishing a Form freezes its render snapshot

Soft Deletes
- Add is_deleted, deleted_at, deleted_by to Event, Form, CanvasLayout, CanvasObject, Lead, Invoice

Migration Notes (v0.2)
- Add Event.timezone (IANA) + end_date
- Introduce Form table; add CanvasLayout.form_id; keep event_id temporarily for backfill
- Lead: add is_test + form_id
- Add EventDayEntitlement for prepaid days; generate invoices from entitlements



