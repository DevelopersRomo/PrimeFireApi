IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'dbo'
      AND TABLE_NAME = 'products'
      AND COLUMN_NAME = 'tax_rate'
      AND (
          DATA_TYPE <> 'decimal'
          OR NUMERIC_PRECISION <> 5
          OR NUMERIC_SCALE <> 2
      )
)
BEGIN
    ALTER TABLE dbo.products
    ALTER COLUMN tax_rate DECIMAL(5,2) NOT NULL;
END;
GO
