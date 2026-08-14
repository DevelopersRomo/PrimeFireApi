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
    DECLARE @default_constraint_name sysname;
    DECLARE @drop_default_sql nvarchar(max);

    SELECT @default_constraint_name = dc.name
    FROM sys.default_constraints AS dc
    INNER JOIN sys.columns AS c
        ON c.object_id = dc.parent_object_id
       AND c.column_id = dc.parent_column_id
    INNER JOIN sys.tables AS t
        ON t.object_id = c.object_id
    INNER JOIN sys.schemas AS s
        ON s.schema_id = t.schema_id
    WHERE s.name = N'dbo'
      AND t.name = N'products'
      AND c.name = N'tax_rate';

    IF @default_constraint_name IS NOT NULL
    BEGIN
        SET @drop_default_sql =
            N'ALTER TABLE dbo.products DROP CONSTRAINT '
            + QUOTENAME(@default_constraint_name)
            + N';';
        EXEC sys.sp_executesql @drop_default_sql;
    END;

    ALTER TABLE dbo.products
    ALTER COLUMN tax_rate DECIMAL(5,2) NOT NULL;
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.default_constraints AS dc
    INNER JOIN sys.columns AS c
        ON c.object_id = dc.parent_object_id
       AND c.column_id = dc.parent_column_id
    INNER JOIN sys.tables AS t
        ON t.object_id = c.object_id
    INNER JOIN sys.schemas AS s
        ON s.schema_id = t.schema_id
    WHERE s.name = N'dbo'
      AND t.name = N'products'
      AND c.name = N'tax_rate'
)
BEGIN
    ALTER TABLE dbo.products
    ADD CONSTRAINT DF_products_tax_rate DEFAULT ((0)) FOR tax_rate;
END;
GO
