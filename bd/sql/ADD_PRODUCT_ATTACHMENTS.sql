IF OBJECT_ID('dbo.product_attachments', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_attachments (
        product_attachment_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        product_id INT NOT NULL,
        file_name NVARCHAR(255) NOT NULL,
        file_type NVARCHAR(100) NULL,
        file_path NVARCHAR(500) NULL,
        created_at DATETIME2 NOT NULL CONSTRAINT DF_product_attachments_created_at DEFAULT (SYSUTCDATETIME()),
        created_by INT NOT NULL,
        CONSTRAINT FK_product_attachments_product
            FOREIGN KEY (product_id)
            REFERENCES dbo.products(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_product_attachments_employee
            FOREIGN KEY (created_by)
            REFERENCES dbo.employees(employee_id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_product_attachments_product_id'
      AND object_id = OBJECT_ID('dbo.product_attachments')
)
BEGIN
    CREATE INDEX IX_product_attachments_product_id
        ON dbo.product_attachments(product_id);
END;
GO
