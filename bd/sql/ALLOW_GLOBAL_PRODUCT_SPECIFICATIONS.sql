IF EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_product_specifications_product_id'
      AND object_id = OBJECT_ID('dbo.product_specifications')
)
BEGIN
    DROP INDEX UX_product_specifications_product_id ON dbo.product_specifications;
END;
GO

IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.product_specifications')
      AND name = 'product_id'
      AND is_nullable = 0
)
BEGIN
    ALTER TABLE dbo.product_specifications
    ALTER COLUMN product_id INT NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_product_specifications_product_id_not_null'
      AND object_id = OBJECT_ID('dbo.product_specifications')
)
BEGIN
    CREATE UNIQUE INDEX UX_product_specifications_product_id_not_null
        ON dbo.product_specifications(product_id)
        WHERE product_id IS NOT NULL;
END;
GO
