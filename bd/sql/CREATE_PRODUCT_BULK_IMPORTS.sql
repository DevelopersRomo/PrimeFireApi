-- Bulk import/export of products: job header, per-row detail, and the
-- products.updated_at column used to detect edits made after an export.

IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.products') AND name = 'updated_at'
)
BEGIN
    ALTER TABLE dbo.products ADD updated_at DATETIME NULL;
END;
GO

IF OBJECT_ID('dbo.product_bulk_imports', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_bulk_imports (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        file_name NVARCHAR(255) NOT NULL,
        stored_path NVARCHAR(500) NOT NULL,
        status NVARCHAR(30) NOT NULL CONSTRAINT DF_product_bulk_imports_status DEFAULT ('analyzing'),
        exported_at DATETIME NULL,
        export_scope NVARCHAR(1000) NULL,
        total_rows INT NOT NULL CONSTRAINT DF_product_bulk_imports_total DEFAULT (0),
        create_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_create DEFAULT (0),
        update_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_update DEFAULT (0),
        unchanged_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_unchanged DEFAULT (0),
        error_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_error DEFAULT (0),
        conflict_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_conflict DEFAULT (0),
        unknown_taxonomy NVARCHAR(MAX) NULL,
        create_missing_taxonomy BIT NOT NULL CONSTRAINT DF_product_bulk_imports_cmt DEFAULT (0),
        apply_conflicts BIT NOT NULL CONSTRAINT DF_product_bulk_imports_ac DEFAULT (0),
        created_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_created DEFAULT (0),
        updated_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_updated DEFAULT (0),
        failed_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_failed DEFAULT (0),
        skipped_count INT NOT NULL CONSTRAINT DF_product_bulk_imports_skipped DEFAULT (0),
        error_report_path NVARCHAR(500) NULL,
        failure_reason NVARCHAR(500) NULL,
        created_by INT NOT NULL,
        created_at DATETIME NOT NULL CONSTRAINT DF_product_bulk_imports_created_at DEFAULT (GETUTCDATE()),
        started_at DATETIME NULL,
        finished_at DATETIME NULL,
        heartbeat_at DATETIME NULL,
        CONSTRAINT FK_product_bulk_imports_employee
            FOREIGN KEY (created_by)
            REFERENCES dbo.employees(employee_id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_product_bulk_imports_status'
      AND object_id = OBJECT_ID('dbo.product_bulk_imports')
)
BEGIN
    CREATE INDEX IX_product_bulk_imports_status
        ON dbo.product_bulk_imports(status);
END;
GO

IF OBJECT_ID('dbo.product_bulk_import_rows', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_bulk_import_rows (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        import_id INT NOT NULL,
        row_number INT NOT NULL,
        action NVARCHAR(20) NOT NULL,
        product_id INT NULL,
        code NVARCHAR(100) NULL,
        name NVARCHAR(255) NULL,
        message NVARCHAR(500) NULL,
        CONSTRAINT FK_product_bulk_import_rows_import
            FOREIGN KEY (import_id)
            REFERENCES dbo.product_bulk_imports(id)
            ON DELETE CASCADE
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_product_bulk_import_rows_import_id'
      AND object_id = OBJECT_ID('dbo.product_bulk_import_rows')
)
BEGIN
    CREATE INDEX IX_product_bulk_import_rows_import_id
        ON dbo.product_bulk_import_rows(import_id);
END;
GO
