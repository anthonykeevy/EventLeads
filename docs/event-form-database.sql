\-- 🎯 Database Architecture: Visual Form Builder Platform
\-- 📚 Based on Database Guide Reference, Screenshot, and Enhanced PRD
\-- 👩‍🎨 UX Checkpoints integrated for alignment

\-- ============================
\-- 🔐 Tenant & User Management
\-- ============================

CREATE TABLE Organization (
OrganizationID INT IDENTITY(1,1) PRIMARY KEY,
Name NVARCHAR(200) NOT NULL,
BillingInfo NVARCHAR(MAX) NULL,
Tier NVARCHAR(50) DEFAULT 'Free',
MaxUsers INT DEFAULT 5,
MaxEvents INT DEFAULT 10,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CreatedBy NVARCHAR(100) NOT NULL,
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL
);

CREATE TABLE \[User] (
UserID INT IDENTITY(1,1) PRIMARY KEY,
OrganizationID INT NOT NULL,
Email NVARCHAR(256) NOT NULL,
Role NVARCHAR(50) NOT NULL CHECK (Role IN ('Admin', 'User')),
InvitedBy INT NULL,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CreatedBy NVARCHAR(100) NOT NULL,
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL,
CONSTRAINT FK\_User\_Organization FOREIGN KEY (OrganizationID) REFERENCES Organization(OrganizationID)
);

\-- ============================
\-- 📅 Events & Canvas Layouts
\-- ============================

CREATE TABLE Event (
EventID INT IDENTITY(1,1) PRIMARY KEY,
OrganizationID INT NOT NULL,
Name NVARCHAR(300) NOT NULL,
Status NVARCHAR(50) NOT NULL CHECK (Status IN ('Draft', 'Published')),
StartDate DATE NOT NULL,
DurationDays INT NOT NULL DEFAULT 1,
CreatedBy INT NOT NULL,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL,
CONSTRAINT FK\_Event\_Org FOREIGN KEY (OrganizationID) REFERENCES Organization(OrganizationID)
);

CREATE TABLE CanvasLayout (
CanvasLayoutID INT IDENTITY(1,1) PRIMARY KEY,
EventID INT NOT NULL,
DeviceType NVARCHAR(50) NOT NULL CHECK (DeviceType IN ('Desktop', 'Tablet', 'Mobile')),
AspectRatio NVARCHAR(10) NOT NULL, -- e.g., '16:9', '4:3'
ResolutionX INT NOT NULL,
ResolutionY INT NOT NULL,
ZoomLevel DECIMAL(5,2) NULL,
RevisionNumber INT NOT NULL DEFAULT 1,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CreatedBy NVARCHAR(100) NOT NULL,
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL,
CONSTRAINT FK\_CanvasLayout\_Event FOREIGN KEY (EventID) REFERENCES Event(EventID)
);

CREATE TABLE FormBuilderImage (
ImageID INT IDENTITY(1,1) PRIMARY KEY,
CanvasLayoutID INT NOT NULL,
ImageName NVARCHAR(300) NOT NULL,
Base64Data NVARCHAR(MAX) NOT NULL,
UploadedBy NVARCHAR(100),
UploadedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CONSTRAINT FK\_Image\_CanvasLayout FOREIGN KEY (CanvasLayoutID) REFERENCES CanvasLayout(CanvasLayoutID)
);

\-- ============================
\-- 🧩 Object Typing & Registry
\-- ============================

CREATE TABLE ObjectType (
ObjectTypeID INT IDENTITY(1,1) PRIMARY KEY,
Name NVARCHAR(100) NOT NULL, -- e.g., TextField, DropdownField, etc.
Category NVARCHAR(50) NOT NULL CHECK (Category IN ('Field', 'Decorative')),
IsSystemDefault BIT NOT NULL DEFAULT 1
);

CREATE TABLE CanvasObject (
ObjectID INT IDENTITY(1,1) PRIMARY KEY,
CanvasLayoutID INT NOT NULL,
ObjectTypeID INT NOT NULL,
Label NVARCHAR(300) NULL,
ExportLabel NVARCHAR(300) NULL,
PositionX INT NOT NULL,
PositionY INT NOT NULL,
Width INT NOT NULL,
Height INT NOT NULL,
TabIndex INT NULL,
ZIndex INT DEFAULT 1,
IsVisible BIT NOT NULL DEFAULT 1,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CreatedBy NVARCHAR(100),
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL,
CONSTRAINT FK\_Object\_CanvasLayout FOREIGN KEY (CanvasLayoutID) REFERENCES CanvasLayout(CanvasLayoutID),
CONSTRAINT FK\_Object\_Type FOREIGN KEY (ObjectTypeID) REFERENCES ObjectType(ObjectTypeID)
);

\-- ============================
\-- 🧩 Specialized Object Tables
\-- ============================

CREATE TABLE TextField (
ObjectID INT PRIMARY KEY,
DefaultValue NVARCHAR(500) NULL,
TextColor NVARCHAR(20),
BoxStyle NVARCHAR(100),
IsRequired BIT DEFAULT 0,
CONSTRAINT FK\_TextField\_Object FOREIGN KEY (ObjectID) REFERENCES CanvasObject(ObjectID)
);

CREATE TABLE DropdownField (
ObjectID INT PRIMARY KEY,
Options NVARCHAR(MAX) NOT NULL, -- JSON
DefaultOption NVARCHAR(300),
TextColor NVARCHAR(20),
BoxStyle NVARCHAR(100),
IsRequired BIT DEFAULT 0,
CONSTRAINT FK\_Dropdown\_Object FOREIGN KEY (ObjectID) REFERENCES CanvasObject(ObjectID)
);

\-- ============================
\-- 📝 Lead Submissions
\-- ============================

CREATE TABLE Lead (
LeadID INT IDENTITY(1,1) PRIMARY KEY,
EventID INT NOT NULL,
SubmittedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
SubmissionData NVARCHAR(MAX) NOT NULL, -- JSON
CONSTRAINT FK\_Lead\_Event FOREIGN KEY (EventID) REFERENCES Event(EventID)
);

\-- ============================
\-- 💳 Invoices
\-- ============================

CREATE TABLE Invoice (
InvoiceID INT IDENTITY(1,1) PRIMARY KEY,
OrganizationID INT NOT NULL,
EventID INT NOT NULL,
Amount DECIMAL(10,2) NOT NULL,
Status NVARCHAR(50) NOT NULL CHECK (Status IN ('Pending', 'Paid', 'Failed')),
StripeTransactionID NVARCHAR(200) NULL,
CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
CreatedBy NVARCHAR(100) NOT NULL,
LastUpdated DATETIME2 NULL,
UpdatedBy NVARCHAR(100) NULL,
CONSTRAINT FK\_Invoice\_Event FOREIGN KEY (EventID) REFERENCES Event(EventID),
CONSTRAINT FK\_Invoice\_Org FOREIGN KEY (OrganizationID) REFERENCES Organization(OrganizationID)
);

\-- ============================
\-- 👩‍🎨 UX Alignment Notes
\-- ============================
\-- 1. Ensure snapping/grid alignment logic is supported in frontend, tied to CanvasObject placement.
\-- 2. Device previews require clear UX guidance when multiple CanvasLayouts exist for an Event.
\-- 3. Accessibility: enforce defaults for contrast, tab order, and visible labels.
\-- 4. RevisionNumber maps to undo/redo features; frontend should expose these.
\-- 5. Preview URLs must render 1:1 with CanvasObject data to build user trust.
\
\-- =============================================================
\-- v0.2 Additions and Alterations (align with UI spec updates)
\-- =============================================================
\
-- 1) Event: add timezone and end date for event-day enforcement
ALTER TABLE Event
  ADD Timezone NVARCHAR(64) NOT NULL DEFAULT 'UTC',
      EndDate DATE NULL;
-- NOTE: Prefer StartDate + EndDate; DurationDays is deprecated and may be removed later.
\
-- 2) Forms: first-class entity with statuses and public slug
CREATE TABLE Form (
  FormID INT IDENTITY(1,1) PRIMARY KEY,
  EventID INT NOT NULL,
  Name NVARCHAR(300) NOT NULL,
  Status NVARCHAR(50) NOT NULL CHECK (Status IN ('Draft','ReadyForReview','ProductionEnabled')),
  PublicSlug NVARCHAR(80) NULL,
  CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
  CreatedBy NVARCHAR(100) NULL,
  LastUpdated DATETIME2 NULL,
  UpdatedBy NVARCHAR(100) NULL,
  IsDeleted BIT NOT NULL DEFAULT 0,
  DeletedAt DATETIME2 NULL,
  DeletedBy NVARCHAR(100) NULL,
  CONSTRAINT FK_Form_Event FOREIGN KEY (EventID) REFERENCES Event(EventID),
  CONSTRAINT UQ_Form_PublicSlug UNIQUE (PublicSlug)
);
\
-- 3) CanvasLayout belongs to Form (deprecate EventID over time)
ALTER TABLE CanvasLayout ADD FormID INT NULL;
ALTER TABLE CanvasLayout ADD CONSTRAINT FK_CanvasLayout_Form FOREIGN KEY (FormID) REFERENCES Form(FormID);
-- Recommendation: backfill FormID for existing rows and later drop EventID.
\
-- 4) Lead: flag test submissions and link to Form
ALTER TABLE Lead ADD IsTest BIT NOT NULL DEFAULT 0;
ALTER TABLE Lead ADD FormID INT NULL;
ALTER TABLE Lead ADD CONSTRAINT FK_Lead_Form FOREIGN KEY (FormID) REFERENCES Form(FormID);
\
-- 5) Soft-delete columns across core entities
ALTER TABLE Event ADD IsDeleted BIT NOT NULL DEFAULT 0, DeletedAt DATETIME2 NULL, DeletedBy NVARCHAR(100) NULL;
ALTER TABLE CanvasLayout ADD IsDeleted BIT NOT NULL DEFAULT 0, DeletedAt DATETIME2 NULL, DeletedBy NVARCHAR(100) NULL;
ALTER TABLE CanvasObject ADD IsDeleted BIT NOT NULL DEFAULT 0, DeletedAt DATETIME2 NULL, DeletedBy NVARCHAR(100) NULL;
ALTER TABLE Lead ADD DeletedAt DATETIME2 NULL, DeletedBy NVARCHAR(100) NULL; -- add soft-delete metadata
ALTER TABLE Invoice ADD IsDeleted BIT NOT NULL DEFAULT 0, DeletedAt DATETIME2 NULL, DeletedBy NVARCHAR(100) NULL;
\
-- 6) Usage-based charging per event day (for billing schedule)
CREATE TABLE UsageCharge (
  UsageChargeID INT IDENTITY(1,1) PRIMARY KEY,
  OrganizationID INT NOT NULL,
  EventID INT NOT NULL,
  ChargeDate DATE NOT NULL, -- in event timezone
  Amount DECIMAL(10,2) NOT NULL,
  Source NVARCHAR(50) NOT NULL CHECK (Source IN ('EventDay')),
  CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
  CreatedBy NVARCHAR(100) NULL,
  CONSTRAINT FK_UsageCharge_Org FOREIGN KEY (OrganizationID) REFERENCES Organization(OrganizationID),
  CONSTRAINT FK_UsageCharge_Event FOREIGN KEY (EventID) REFERENCES Event(EventID),
  CONSTRAINT UQ_UsageCharge UNIQUE (EventID, ChargeDate, Source)
);
\
-- 7) Seed default ObjectTypes (example; wrap in IF NOT EXISTS in real migrations)
INSERT INTO ObjectType (Name, Category, IsSystemDefault)
VALUES ('TextField','Field',1), ('DropdownField','Field',1), ('CheckboxField','Field',1);

\-- =============================================================
\-- v0.3 Prepaid Entitlements for Event Days
\-- =============================================================

-- Prepaid entitlements model: one row per purchased event day
CREATE TABLE EventDayEntitlement (
  EventDayEntitlementID INT IDENTITY(1,1) PRIMARY KEY,
  OrganizationID INT NOT NULL,
  EventID INT NOT NULL,
  EntitlementDate DATE NOT NULL,
  Amount DECIMAL(10,2) NOT NULL,
  InvoiceID INT NULL,
  CreatedDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
  CreatedBy NVARCHAR(100) NULL,
  CONSTRAINT FK_Entitlement_Org FOREIGN KEY (OrganizationID) REFERENCES Organization(OrganizationID),
  CONSTRAINT FK_Entitlement_Event FOREIGN KEY (EventID) REFERENCES Event(EventID),
  CONSTRAINT FK_Entitlement_Invoice FOREIGN KEY (InvoiceID) REFERENCES Invoice(InvoiceID),
  CONSTRAINT UQ_Entitlement UNIQUE (EventID, EntitlementDate)
);

-- Note: Keep UsageCharge for accounting/audit if desired; entitlements define access rights.
