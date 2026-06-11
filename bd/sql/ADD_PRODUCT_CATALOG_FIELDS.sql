IF OBJECT_ID('dbo.product_families', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_families (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX) NULL,
        active BIT NOT NULL CONSTRAINT DF_product_families_active DEFAULT (1),
        created_at DATETIME2 NOT NULL CONSTRAINT DF_product_families_created_at DEFAULT (SYSUTCDATETIME())
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UX_product_families_name'
      AND object_id = OBJECT_ID('dbo.product_families')
)
BEGIN
    CREATE UNIQUE INDEX UX_product_families_name
        ON dbo.product_families(name);
END;
GO

IF COL_LENGTH('dbo.product_families', 'created_at') IS NULL
BEGIN
    ALTER TABLE dbo.product_families ADD created_at DATETIME2 NULL;
END;
GO

IF COL_LENGTH('dbo.product_families', 'created_at') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM sys.default_constraints dc
       INNER JOIN sys.columns c ON c.default_object_id = dc.object_id
       WHERE dc.parent_object_id = OBJECT_ID('dbo.product_families')
         AND c.name = 'created_at'
   )
BEGIN
    ALTER TABLE dbo.product_families
        ADD CONSTRAINT DF_product_families_created_at
        DEFAULT (SYSUTCDATETIME()) FOR created_at;
END;
GO

UPDATE dbo.product_families
SET created_at = SYSUTCDATETIME()
WHERE created_at IS NULL;
GO

IF OBJECT_ID('dbo.product_categories', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_categories (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        family_id INT NOT NULL,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX) NULL,
        active BIT NOT NULL CONSTRAINT DF_product_categories_active DEFAULT (1),
        CONSTRAINT FK_product_categories_family
            FOREIGN KEY (family_id)
            REFERENCES dbo.product_families(id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UX_product_categories_family_name'
      AND object_id = OBJECT_ID('dbo.product_categories')
)
BEGIN
    CREATE UNIQUE INDEX UX_product_categories_family_name
        ON dbo.product_categories(family_id, name);
END;
GO

IF OBJECT_ID('dbo.product_catalog', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_catalog (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        code NVARCHAR(50) NOT NULL,
        name NVARCHAR(255) NOT NULL,
        family_id INT NULL,
        category_id INT NULL,
        unit NVARCHAR(20) NULL,
        min_stock DECIMAL(12,2) NOT NULL CONSTRAINT DF_product_catalog_min_stock DEFAULT (0),
        active BIT NOT NULL CONSTRAINT DF_product_catalog_active DEFAULT (1),
        description NVARCHAR(MAX) NULL,
        created_at DATETIME2 NOT NULL CONSTRAINT DF_product_catalog_created_at DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT FK_product_catalog_family
            FOREIGN KEY (family_id)
            REFERENCES dbo.product_families(id),
        CONSTRAINT FK_product_catalog_category
            FOREIGN KEY (category_id)
            REFERENCES dbo.product_categories(id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UX_product_catalog_code'
      AND object_id = OBJECT_ID('dbo.product_catalog')
)
BEGIN
    CREATE UNIQUE INDEX UX_product_catalog_code
        ON dbo.product_catalog(code);
END;
GO

IF OBJECT_ID('dbo.product_specifications', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.product_specifications (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        product_id INT NOT NULL,
        specification NVARCHAR(100) NULL,
        size NVARCHAR(100) NULL,
        material NVARCHAR(100) NULL,
        manufacturer NVARCHAR(100) NULL,
        model NVARCHAR(100) NULL,
        notes NVARCHAR(MAX) NULL,
        CONSTRAINT FK_product_specifications_product
            FOREIGN KEY (product_id)
            REFERENCES dbo.product_catalog(id)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UX_product_specifications_product_id'
      AND object_id = OBJECT_ID('dbo.product_specifications')
)
BEGIN
    CREATE UNIQUE INDEX UX_product_specifications_product_id
        ON dbo.product_specifications(product_id);
END;
GO

INSERT INTO dbo.product_families (name, description, active, created_at)
SELECT 'Fire Alarm', NULL, 1, SYSUTCDATETIME()
WHERE NOT EXISTS (SELECT 1 FROM dbo.product_families WHERE name = 'Fire Alarm');

INSERT INTO dbo.product_families (name, description, active, created_at)
SELECT 'Plumbing', NULL, 1, SYSUTCDATETIME()
WHERE NOT EXISTS (SELECT 1 FROM dbo.product_families WHERE name = 'Plumbing');

INSERT INTO dbo.product_families (name, description, active, created_at)
SELECT 'Fire Sprinkler', NULL, 1, SYSUTCDATETIME()
WHERE NOT EXISTS (SELECT 1 FROM dbo.product_families WHERE name = 'Fire Sprinkler');

INSERT INTO dbo.product_families (name, description, active, created_at)
SELECT 'Security', NULL, 1, SYSUTCDATETIME()
WHERE NOT EXISTS (SELECT 1 FROM dbo.product_families WHERE name = 'Security');
GO

INSERT INTO dbo.product_categories (family_id, name, description, active)
SELECT pf.id, 'Device', NULL, 1
FROM dbo.product_families pf
WHERE pf.name = 'Fire Alarm'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.product_categories pc
      WHERE pc.family_id = pf.id AND pc.name = 'Device'
  );

INSERT INTO dbo.product_categories (family_id, name, description, active)
SELECT pf.id, 'Module', NULL, 1
FROM dbo.product_families pf
WHERE pf.name = 'Fire Alarm'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.product_categories pc
      WHERE pc.family_id = pf.id AND pc.name = 'Module'
  );

INSERT INTO dbo.product_categories (family_id, name, description, active)
SELECT pf.id, 'Valve', NULL, 1
FROM dbo.product_families pf
WHERE pf.name = 'Plumbing'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.product_categories pc
      WHERE pc.family_id = pf.id AND pc.name = 'Valve'
  );

INSERT INTO dbo.product_categories (family_id, name, description, active)
SELECT pf.id, 'Head', NULL, 1
FROM dbo.product_families pf
WHERE pf.name = 'Fire Sprinkler'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.product_categories pc
      WHERE pc.family_id = pf.id AND pc.name = 'Head'
  );
GO

WITH product_source AS (
    SELECT
        p.*,
        CASE
            WHEN NULLIF(LTRIM(RTRIM(p.code)), '') IS NOT NULL
                 AND UPPER(LTRIM(RTRIM(p.code))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                THEN LTRIM(RTRIM(p.code))
            WHEN NULLIF(LTRIM(RTRIM(p.sku)), '') IS NOT NULL
                 AND UPPER(LTRIM(RTRIM(p.sku))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                THEN LTRIM(RTRIM(p.sku))
            ELSE CONCAT('P-', p.id)
        END AS base_catalog_code
    FROM dbo.products p
),
product_codes AS (
    SELECT
        ps.*,
        CASE
            WHEN COUNT(*) OVER (PARTITION BY ps.base_catalog_code) > 1
                THEN CONCAT(LEFT(ps.base_catalog_code, 40), '-', ps.id)
            ELSE ps.base_catalog_code
        END AS catalog_code
    FROM product_source ps
)
INSERT INTO dbo.product_catalog (code, name, family_id, category_id, unit, min_stock, active, description, created_at)
SELECT
    pcodes.catalog_code,
    pcodes.name,
    pcodes.family_id,
    pcodes.category_id,
    LEFT(pcodes.unit, 20),
    COALESCE(pcodes.min_stock, 0),
    pcodes.is_active,
    pcodes.description,
    COALESCE(pcodes.created_at, SYSUTCDATETIME())
FROM product_codes pcodes
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.product_catalog pc
    WHERE pc.code = pcodes.catalog_code
);
GO

INSERT INTO dbo.product_specifications (
    product_id,
    specification,
    size,
    material,
    manufacturer,
    model,
    notes
)
SELECT
    pc.id,
    p.specification,
    p.size,
    p.material_type,
    p.manufacturer,
    p.model,
    NULL
FROM dbo.products p
CROSS APPLY (
    SELECT
        CASE
            WHEN NULLIF(LTRIM(RTRIM(p.code)), '') IS NOT NULL
                 AND UPPER(LTRIM(RTRIM(p.code))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                THEN LTRIM(RTRIM(p.code))
            WHEN NULLIF(LTRIM(RTRIM(p.sku)), '') IS NOT NULL
                 AND UPPER(LTRIM(RTRIM(p.sku))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                THEN LTRIM(RTRIM(p.sku))
            ELSE CONCAT('P-', p.id)
        END AS base_catalog_code
) base_code
CROSS APPLY (
    SELECT
        CASE
            WHEN (
                SELECT COUNT(*)
                FROM dbo.products p2
                CROSS APPLY (
                    SELECT
                        CASE
                            WHEN NULLIF(LTRIM(RTRIM(p2.code)), '') IS NOT NULL
                                 AND UPPER(LTRIM(RTRIM(p2.code))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                                THEN LTRIM(RTRIM(p2.code))
                            WHEN NULLIF(LTRIM(RTRIM(p2.sku)), '') IS NOT NULL
                                 AND UPPER(LTRIM(RTRIM(p2.sku))) NOT IN ('NA', 'N/A', 'NONE', 'NULL')
                                THEN LTRIM(RTRIM(p2.sku))
                            ELSE CONCAT('P-', p2.id)
                        END AS base_catalog_code
                ) bc2
                WHERE bc2.base_catalog_code = base_code.base_catalog_code
            ) > 1
                THEN CONCAT(LEFT(base_code.base_catalog_code, 40), '-', p.id)
            ELSE base_code.base_catalog_code
        END AS catalog_code
) resolved_code
INNER JOIN dbo.product_catalog pc
    ON pc.code = resolved_code.catalog_code
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.product_specifications ps
    WHERE ps.product_id = pc.id
);
GO
