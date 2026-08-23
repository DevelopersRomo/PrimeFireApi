/* =============================================================================
   Travel Expense Reimbursement module (Viaticos)
   SQL Server DDL + seed data

   Run once per tenant database. Every statement is guarded, so re-running is
   safe and will not drop or overwrite existing data.

   Sections:
     1. Tables
     2. Indexes
     3. Module registration (sidebar entry)
     4. Approver roles (creates Accountant; Manager is expected to exist)
     5. Role permissions
     6. Expense categories (seed - EDIT THE CAPS)
     7. Approval chain: Manager (level 1) -> Accountant (level 2)
   ============================================================================= */

SET NOCOUNT ON;
GO

/* ---------------------------------------------------------------------------
   1. Tables
   --------------------------------------------------------------------------- */

IF OBJECT_ID('dbo.expense_categories', 'U') IS NULL
CREATE TABLE dbo.expense_categories (
    category_id       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name              NVARCHAR(100)  NOT NULL,
    code              NVARCHAR(30)   NULL,
    requires_invoice  BIT            NOT NULL CONSTRAINT DF_expense_categories_req DEFAULT (0),
    per_item_cap      DECIMAL(18,2)  NULL,
    daily_cap         DECIMAL(18,2)  NULL,
    display_order     INT            NOT NULL CONSTRAINT DF_expense_categories_ord DEFAULT (0),
    is_active         BIT            NOT NULL CONSTRAINT DF_expense_categories_act DEFAULT (1)
);
GO

IF OBJECT_ID('dbo.expense_approval_rules', 'U') IS NULL
CREATE TABLE dbo.expense_approval_rules (
    rule_id     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    min_amount  DECIMAL(18,2) NOT NULL CONSTRAINT DF_expense_rules_min DEFAULT (0),
    max_amount  DECIMAL(18,2) NULL,                      -- NULL means no upper bound
    level       INT           NOT NULL CONSTRAINT DF_expense_rules_lvl DEFAULT (1),
    role_id     INT           NOT NULL,
    is_active   BIT           NOT NULL CONSTRAINT DF_expense_rules_act DEFAULT (1),
    CONSTRAINT FK_expense_rules_role FOREIGN KEY (role_id) REFERENCES dbo.roles(role_id)
);
GO

IF OBJECT_ID('dbo.expense_reports', 'U') IS NULL
CREATE TABLE dbo.expense_reports (
    report_id         INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    folio             NVARCHAR(30)   NOT NULL,
    employee_id       INT            NOT NULL,
    job_id            INT            NULL,
    title             NVARCHAR(200)  NOT NULL,
    po_number         NVARCHAR(100)  NULL,
    project           NVARCHAR(150)  NULL,
    trip_type         NVARCHAR(20)   NOT NULL CONSTRAINT DF_expense_reports_type DEFAULT ('national'),
    destination       NVARCHAR(200)  NULL,
    trip_start_date   DATE           NULL,
    trip_end_date     DATE           NULL,
    currency          NVARCHAR(3)    NOT NULL CONSTRAINT DF_expense_reports_cur DEFAULT ('USD'),
    total_requested   DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_reports_req DEFAULT (0),
    total_approved    DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_reports_app DEFAULT (0),
    total_reimbursed  DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_reports_rei DEFAULT (0),
    status            NVARCHAR(25)   NOT NULL CONSTRAINT DF_expense_reports_st  DEFAULT ('draft'),
    current_level     INT            NOT NULL CONSTRAINT DF_expense_reports_lvl DEFAULT (0),
    notes             NVARCHAR(2000) NULL,
    submitted_at      DATETIME       NULL,
    created_at        DATETIME       NOT NULL CONSTRAINT DF_expense_reports_cre DEFAULT (GETUTCDATE()),
    updated_at        DATETIME       NOT NULL CONSTRAINT DF_expense_reports_upd DEFAULT (GETUTCDATE()),
    CONSTRAINT UQ_expense_reports_folio UNIQUE (folio),
    CONSTRAINT FK_expense_reports_emp FOREIGN KEY (employee_id) REFERENCES dbo.employees(employee_id),
    CONSTRAINT FK_expense_reports_job FOREIGN KEY (job_id)      REFERENCES dbo.jobs(job_id),
    CONSTRAINT CK_expense_reports_status CHECK (status IN
        ('draft','submitted','in_review','approved','partially_approved','rejected','paid','cancelled')),
    CONSTRAINT CK_expense_reports_trip CHECK (trip_type IN ('national','international'))
);
GO

IF OBJECT_ID('dbo.expense_report_items', 'U') IS NULL
CREATE TABLE dbo.expense_report_items (
    item_id                INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id              INT            NOT NULL,
    category_id            INT            NULL,
    expense_date           DATE           NULL,
    merchant               NVARCHAR(200)  NULL,
    description            NVARCHAR(500)  NULL,
    currency               NVARCHAR(3)    NOT NULL CONSTRAINT DF_expense_items_cur DEFAULT ('USD'),
    amount_original        DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_items_amt DEFAULT (0),
    fx_rate                DECIMAL(18,6)  NOT NULL CONSTRAINT DF_expense_items_fx  DEFAULT (1),
    amount_base            DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_items_bas DEFAULT (0),
    subtotal_amount        DECIMAL(18,2)  NULL,
    tax_amount             DECIMAL(18,2)  NULL,
    tip_amount             DECIMAL(18,2)  NULL,
    has_invoice            BIT            NOT NULL CONSTRAINT DF_expense_items_inv DEFAULT (0),
    tax_id                 NVARCHAR(20)   NULL,
    status                 NVARCHAR(20)   NOT NULL CONSTRAINT DF_expense_items_st  DEFAULT ('pending'),
    approved_amount        DECIMAL(18,2)  NULL,
    review_note            NVARCHAR(500)  NULL,
    source                 NVARCHAR(20)   NOT NULL CONSTRAINT DF_expense_items_src DEFAULT ('manual'),
    extraction_confidence  DECIMAL(5,4)   NULL,
    created_at             DATETIME       NOT NULL CONSTRAINT DF_expense_items_cre DEFAULT (GETUTCDATE()),
    updated_at             DATETIME       NOT NULL CONSTRAINT DF_expense_items_upd DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_items_report   FOREIGN KEY (report_id)   REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_items_category FOREIGN KEY (category_id) REFERENCES dbo.expense_categories(category_id),
    CONSTRAINT CK_expense_items_status CHECK (status IN ('pending','approved','rejected')),
    CONSTRAINT CK_expense_items_source CHECK (source IN ('manual','ocr','qr','pdf_text'))
);
GO

IF OBJECT_ID('dbo.expense_receipts', 'U') IS NULL
CREATE TABLE dbo.expense_receipts (
    receipt_id   INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id    INT            NOT NULL,
    item_id      INT            NULL,
    file_name    NVARCHAR(255)  NOT NULL,
    file_type    NVARCHAR(100)  NULL,
    file_path    NVARCHAR(500)  NULL,
    file_size    INT            NULL,
    sha256       NVARCHAR(64)   NULL,   -- identical file re-uploaded
    phash        NVARCHAR(32)   NULL,   -- same photo, recropped or re-encoded
    page_count   INT            NOT NULL CONSTRAINT DF_expense_receipts_pc DEFAULT (1),
    uploaded_by  INT            NULL,
    created_at   DATETIME       NOT NULL CONSTRAINT DF_expense_receipts_cre DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_receipts_report FOREIGN KEY (report_id)   REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_receipts_item   FOREIGN KEY (item_id)     REFERENCES dbo.expense_report_items(item_id),
    CONSTRAINT FK_expense_receipts_emp    FOREIGN KEY (uploaded_by) REFERENCES dbo.employees(employee_id)
);
GO

IF OBJECT_ID('dbo.expense_receipt_extractions', 'U') IS NULL
CREATE TABLE dbo.expense_receipt_extractions (
    extraction_id      INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    receipt_id         INT            NOT NULL,
    engine             NVARCHAR(20)   NULL,   -- qr_sat, pdf_text, tesseract
    status             NVARCHAR(20)   NOT NULL CONSTRAINT DF_expense_extr_st DEFAULT ('pending'),
    raw_text           NVARCHAR(MAX)  NULL,
    detected_total     DECIMAL(18,2)  NULL,
    detected_subtotal  DECIMAL(18,2)  NULL,
    detected_tax       DECIMAL(18,2)  NULL,
    detected_tip       DECIMAL(18,2)  NULL,
    detected_currency  NVARCHAR(3)    NULL,
    detected_date      DATE           NULL,
    detected_merchant  NVARCHAR(200)  NULL,
    detected_tax_id    NVARCHAR(20)   NULL,
    detected_uuid      NVARCHAR(36)   NULL,   -- CFDI UUID: exact duplicate detection
    confidence         DECIMAL(5,4)   NOT NULL CONSTRAINT DF_expense_extr_conf DEFAULT (0),
    arithmetic_ok      BIT            NOT NULL CONSTRAINT DF_expense_extr_ar   DEFAULT (0),
    candidates_json    NVARCHAR(MAX)  NULL,   -- top candidates with score + bounding box
    error_message      NVARCHAR(500)  NULL,
    duration_ms        INT            NULL,
    processed_at       DATETIME       NULL,
    created_at         DATETIME       NOT NULL CONSTRAINT DF_expense_extr_cre DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_extr_receipt FOREIGN KEY (receipt_id) REFERENCES dbo.expense_receipts(receipt_id)
);
GO

IF OBJECT_ID('dbo.expense_report_approvals', 'U') IS NULL
CREATE TABLE dbo.expense_report_approvals (
    approval_id      INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id        INT            NOT NULL,
    level            INT            NOT NULL CONSTRAINT DF_expense_appr_lvl DEFAULT (1),
    role_id          INT            NULL,
    approver_id      INT            NULL,
    decision         NVARCHAR(25)   NOT NULL CONSTRAINT DF_expense_appr_dec DEFAULT ('pending'),
    amount_approved  DECIMAL(18,2)  NULL,
    note             NVARCHAR(1000) NULL,
    decided_at       DATETIME       NULL,
    created_at       DATETIME       NOT NULL CONSTRAINT DF_expense_appr_cre DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_appr_report FOREIGN KEY (report_id)   REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_appr_role   FOREIGN KEY (role_id)     REFERENCES dbo.roles(role_id),
    CONSTRAINT FK_expense_appr_emp    FOREIGN KEY (approver_id) REFERENCES dbo.employees(employee_id),
    CONSTRAINT CK_expense_appr_decision CHECK (decision IN
        ('pending','approved','partially_approved','rejected'))
);
GO

IF OBJECT_ID('dbo.expense_report_flags', 'U') IS NULL
CREATE TABLE dbo.expense_report_flags (
    flag_id     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id   INT           NOT NULL,
    item_id     INT           NULL,
    code        NVARCHAR(40)  NOT NULL,
    severity    NVARCHAR(10)  NOT NULL CONSTRAINT DF_expense_flags_sev DEFAULT ('warning'),
    message     NVARCHAR(500) NOT NULL,
    created_at  DATETIME      NOT NULL CONSTRAINT DF_expense_flags_cre DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_flags_report FOREIGN KEY (report_id) REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_flags_item   FOREIGN KEY (item_id)   REFERENCES dbo.expense_report_items(item_id),
    CONSTRAINT CK_expense_flags_severity CHECK (severity IN ('info','warning','critical'))
);
GO

IF OBJECT_ID('dbo.expense_report_messages', 'U') IS NULL
CREATE TABLE dbo.expense_report_messages (
    message_id   INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id    INT           NOT NULL,
    user_id      INT           NOT NULL,
    message_txt  NVARCHAR(MAX) NULL,
    created_at   DATETIME      NOT NULL CONSTRAINT DF_expense_msg_cre DEFAULT (GETUTCDATE()),
    updated_at   DATETIME      NULL,
    edited_at    DATETIME      NULL,
    CONSTRAINT FK_expense_msg_report FOREIGN KEY (report_id) REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_msg_user   FOREIGN KEY (user_id)   REFERENCES dbo.employees(employee_id)
);
GO

IF OBJECT_ID('dbo.expense_reimbursements', 'U') IS NULL
CREATE TABLE dbo.expense_reimbursements (
    reimbursement_id  INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    report_id         INT            NOT NULL,
    amount            DECIMAL(18,2)  NOT NULL CONSTRAINT DF_expense_reim_amt DEFAULT (0),
    currency          NVARCHAR(3)    NOT NULL CONSTRAINT DF_expense_reim_cur DEFAULT ('USD'),
    payment_method    NVARCHAR(50)   NULL,
    reference         NVARCHAR(100)  NULL,
    note              NVARCHAR(500)  NULL,
    paid_by           INT            NULL,
    paid_at           DATETIME       NOT NULL CONSTRAINT DF_expense_reim_at DEFAULT (GETUTCDATE()),
    CONSTRAINT FK_expense_reim_report FOREIGN KEY (report_id) REFERENCES dbo.expense_reports(report_id),
    CONSTRAINT FK_expense_reim_emp    FOREIGN KEY (paid_by)   REFERENCES dbo.employees(employee_id)
);
GO

/* ---------------------------------------------------------------------------
   2. Indexes
   --------------------------------------------------------------------------- */

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_reports_employee')
    CREATE INDEX IX_expense_reports_employee ON dbo.expense_reports (employee_id, status);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_reports_status')
    CREATE INDEX IX_expense_reports_status ON dbo.expense_reports (status, created_at DESC);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_items_report')
    CREATE INDEX IX_expense_items_report ON dbo.expense_report_items (report_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_receipts_report')
    CREATE INDEX IX_expense_receipts_report ON dbo.expense_receipts (report_id);
GO
-- Deduplication lookups hit these two constantly.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_receipts_sha256')
    CREATE INDEX IX_expense_receipts_sha256 ON dbo.expense_receipts (sha256);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_extr_receipt')
    CREATE INDEX IX_expense_extr_receipt ON dbo.expense_receipt_extractions (receipt_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_extr_uuid')
    CREATE INDEX IX_expense_extr_uuid ON dbo.expense_receipt_extractions (detected_uuid);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_appr_report')
    CREATE INDEX IX_expense_appr_report ON dbo.expense_report_approvals (report_id, decision);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_flags_report')
    CREATE INDEX IX_expense_flags_report ON dbo.expense_report_flags (report_id);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_expense_msg_report')
    CREATE INDEX IX_expense_msg_report ON dbo.expense_report_messages (report_id, created_at);
GO

/* ---------------------------------------------------------------------------
   3. Module registration
      Adds "Expenses" to the sidebar under Workforce Management.
   --------------------------------------------------------------------------- */

DECLARE @parent_module_id INT = (
    SELECT TOP 1 module_id FROM dbo.modules
    WHERE module_key IN ('workforce_management','workforce','workforce-management')
);

IF NOT EXISTS (SELECT 1 FROM dbo.modules WHERE module_key = 'expenses')
BEGIN
    INSERT INTO dbo.modules (module_name, module_key, description, icon, route_url, display_order, is_active, parent_module_id, created_at)
    VALUES ('Expenses', 'expenses', 'Travel expense reimbursement', 'receipt_long', '/expenses', 40, 1,
            @parent_module_id, CONVERT(NVARCHAR(19), GETUTCDATE(), 120));
END
GO

/* ---------------------------------------------------------------------------
   4. Approver roles

   The chain has exactly two levels: Manager first, then Accountant. Manager
   already exists in this tenant, so only the accountant role is created here.

   EDIT the names if this tenant spells them differently.
   --------------------------------------------------------------------------- */

IF NOT EXISTS (SELECT 1 FROM dbo.roles WHERE role_name IN ('Accountant', 'Contador'))
    INSERT INTO dbo.roles (role_name, description)
    VALUES ('Accountant', 'Reviews and pays approved expense reimbursements');
GO

/* ---------------------------------------------------------------------------
   5. Role permissions

   Everyone files their own claims. Approvers need nothing extra to approve:
   the chain grants that by role. admin_actions is separate and unlocks
   reimbursing and configuring, so it goes to the accountant and to admins.
   --------------------------------------------------------------------------- */

DECLARE @expenses_module_id INT = (SELECT module_id FROM dbo.modules WHERE module_key = 'expenses');

-- Everyone files their own reports.
INSERT INTO dbo.role_modules (role_id, module_id, can_view, can_create, can_edit, can_delete, can_export, admin_actions, other_actions, assigned_at)
SELECT r.role_id, @expenses_module_id, 1, 1, 1, 1, 0, 0, 0, GETUTCDATE()
FROM dbo.roles r
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.role_modules rm
    WHERE rm.role_id = r.role_id AND rm.module_id = @expenses_module_id
);
GO

-- Accountants and administrators reimburse, export and configure.
-- Note: admin_actions lets someone stand in for an absent approver, but it can
-- never approve their own report, and never both levels of the same report.
DECLARE @expenses_module_id INT = (SELECT module_id FROM dbo.modules WHERE module_key = 'expenses');

UPDATE rm
SET rm.admin_actions = 1, rm.can_export = 1
FROM dbo.role_modules rm
INNER JOIN dbo.roles r ON r.role_id = rm.role_id
WHERE rm.module_id = @expenses_module_id
  AND r.role_name IN ('Admin', 'Administrator', 'Administrador',   -- EDIT
                      'Accountant', 'Contador');
GO

/* ---------------------------------------------------------------------------
   6. Expense categories

   ALL CAPS ARE IN USD, the base currency. A line captured in another currency is
   converted with its fx_rate before the cap is compared, so one cap per category
   covers Mexico, the Dominican Republic and Puerto Rico alike.

   per_item_cap and daily_cap are what the policy engine enforces. NULL means no
   cap. requires_invoice = 1 flags any line in that category with no fiscal
   invoice attached.

   Keep per_item_cap <= daily_cap, otherwise a single expense can clear the
   per-item rule while already breaking the daily one.

   THESE ARE STARTING VALUES. Adjust them to your actual policy.
   --------------------------------------------------------------------------- */

MERGE dbo.expense_categories AS target
USING (VALUES
    ('Transport', 'TRANSPORT', 0, NULL,   NULL,   10),
    ('Lodging',   'LODGING',   1, NULL,   200.00, 20),   -- per night
    ('Meals',     'MEALS',     0, 40.00,   90.00, 30),   -- per meal / per day
    ('Fuel',      'FUEL',      1, NULL,   NULL,   40),
    ('Tolls',     'TOLLS',     0, NULL,   NULL,   50),
    ('Other',     'OTHER',     0, NULL,   NULL,   60)
) AS source (name, code, requires_invoice, per_item_cap, daily_cap, display_order)
ON target.code = source.code
WHEN NOT MATCHED BY TARGET THEN
    INSERT (name, code, requires_invoice, per_item_cap, daily_cap, display_order, is_active)
    VALUES (source.name, source.code, source.requires_invoice, source.per_item_cap,
            source.daily_cap, source.display_order, 1);
GO

/* ---------------------------------------------------------------------------
   7. Approval chain

   Every report, whatever the amount, needs two approvals:

       level 1  ->  Manager
       level 2  ->  Accountant

   One amount band from 0 to unbounded (max_amount NULL) covers everything, so
   no threshold has to be maintained.

   The table still supports amount tiers if the policy ever changes: give the
   band an upper bound and add a second band above it. The API reads whichever
   rows match the report total, so that is a data change, not a code change.
   --------------------------------------------------------------------------- */

DECLARE @manager_role_id    INT = (SELECT TOP 1 role_id FROM dbo.roles WHERE role_name IN ('Manager','Gerente'));         -- EDIT
DECLARE @accountant_role_id INT = (SELECT TOP 1 role_id FROM dbo.roles WHERE role_name IN ('Accountant','Contador'));     -- EDIT

IF @manager_role_id IS NULL OR @accountant_role_id IS NULL
    PRINT 'Approval chain SKIPPED: Manager or Accountant role not found. Check the role names above.';
ELSE IF EXISTS (SELECT 1 FROM dbo.expense_approval_rules)
    PRINT 'Approval chain SKIPPED: rules already exist. Maintain them in the admin UI.';
ELSE
BEGIN
    -- Level 1: the requester's manager decides whether the expense was justified.
    INSERT INTO dbo.expense_approval_rules (min_amount, max_amount, level, role_id, is_active)
    VALUES (0, NULL, 1, @manager_role_id, 1);

    -- Level 2: the accountant decides whether it is properly documented, then pays.
    INSERT INTO dbo.expense_approval_rules (min_amount, max_amount, level, role_id, is_active)
    VALUES (0, NULL, 2, @accountant_role_id, 1);

    PRINT 'Approval chain created: Manager (level 1) -> Accountant (level 2).';
END
GO

PRINT 'Expenses module installed.';
GO
