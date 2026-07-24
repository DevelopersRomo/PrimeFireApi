-- Sets the configured PDF title for the QR quotation template.
-- The apostrophe in Romo's is escaped for SQL Server.

UPDATE it.pdf_templates
SET document_title = N'Developers Romo''s'
WHERE tenant_id = 1
  AND template_key = N'Quotation_QR';

PRINT 'QR PDF template title set to Developers Romo''s.';
