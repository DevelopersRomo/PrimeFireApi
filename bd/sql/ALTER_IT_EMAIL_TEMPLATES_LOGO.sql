-- Adds the uploaded-logo path for default and customer IT email templates.
-- Safe to run multiple times.

SET NOCOUNT ON;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('it.email_defaults')
      AND name = 'logo_path'
)
BEGIN
    ALTER TABLE it.email_defaults
        ADD logo_path NVARCHAR(1000) NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('it.email_customer_templates')
      AND name = 'logo_path'
)
BEGIN
    ALTER TABLE it.email_customer_templates
        ADD logo_path NVARCHAR(1000) NULL;
END;
GO

PRINT 'logo_path added to IT email templates.';
GO
