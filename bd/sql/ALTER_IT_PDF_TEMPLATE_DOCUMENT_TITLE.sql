-- Add `document_title` to it.pdf_templates so the PDF header text
-- ("IT Solutions Quotation") is configurable per template.
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
