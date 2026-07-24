-- Add `header_color` (hex string) to both email template tables so tenants can
-- customize the ticket-style header banner in the quotation email.
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
