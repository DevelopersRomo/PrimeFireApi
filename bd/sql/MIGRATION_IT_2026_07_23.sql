-- =============================================================================
-- IT module migration bundle (2026-07-23)
-- Combines three independent migrations so they can be executed in a single run:
--   1. it.pdf_templates.document_title
--   2. it.email_defaults.header_color + it.email_customer_templates.header_color
--   3. it.customer_quotation_sequences (new table)
-- All statements are idempotent — safe to run multiple times.
-- =============================================================================

SET NOCOUNT ON;
GO

-- -----------------------------------------------------------------------------
-- 1. it.pdf_templates.document_title
--    Makes the PDF header text ("IT Solutions Quotation") configurable per
--    template.
-- -----------------------------------------------------------------------------
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('it.pdf_templates')
      AND name = 'document_title'
)
BEGIN
    ALTER TABLE it.pdf_templates
        ADD document_title NVARCHAR(200) NULL;
END;
GO

PRINT 'Column document_title added to it.pdf_templates.';
GO

-- -----------------------------------------------------------------------------
-- 2. it.email_defaults.header_color + it.email_customer_templates.header_color
--    Adds a hex-string color used as the ticket-style header banner for the
--    quotation emails. Present on both the tenant default and per-customer
--    overrides.
-- -----------------------------------------------------------------------------
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('it.email_defaults')
      AND name = 'header_color'
)
BEGIN
    ALTER TABLE it.email_defaults
        ADD header_color NVARCHAR(20) NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('it.email_customer_templates')
      AND name = 'header_color'
)
BEGIN
    ALTER TABLE it.email_customer_templates
        ADD header_color NVARCHAR(20) NULL;
END;
GO

PRINT 'header_color added to it.email_defaults and it.email_customer_templates.';
GO

-- -----------------------------------------------------------------------------
-- 3. it.customer_quotation_sequences
--    Per-customer counter used to number quotations at send time.
--    Format assigned on first send: Q-{FIRST3(customer_name)}-{customer_id}-{seq:05d}
--    Existing Q-IT-{year}-{seq} numbers are preserved and remain valid.
-- -----------------------------------------------------------------------------
IF OBJECT_ID('it.customer_quotation_sequences', 'U') IS NULL
BEGIN
    CREATE TABLE it.customer_quotation_sequences (
        tenant_id   INT NOT NULL,
        customer_id INT NOT NULL,
        last_number INT NOT NULL DEFAULT 0,
        updated_at  DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_customer_quotation_sequences
            PRIMARY KEY (tenant_id, customer_id)
    );
END;
GO

PRINT 'it.customer_quotation_sequences created.';
GO

PRINT 'IT module migration 2026-07-23 completed.';
GO
