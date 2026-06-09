IF NOT EXISTS (
    SELECT 1
    FROM sys.tables t
    INNER JOIN sys.schemas s ON s.schema_id = t.schema_id
    WHERE t.name = 'warehouse_locations'
      AND s.name = 'dbo'
)
BEGIN
    CREATE TABLE dbo.warehouse_locations (
        warehouse_location_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        name NVARCHAR(200) NOT NULL,
        is_active BIT NOT NULL CONSTRAINT DF_warehouse_locations_is_active DEFAULT (1)
    );

    CREATE UNIQUE INDEX UX_warehouse_locations_name
        ON dbo.warehouse_locations(name);
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_warehouse_locations_name'
      AND object_id = OBJECT_ID('dbo.warehouse_locations')
)
BEGIN
    CREATE UNIQUE INDEX UX_warehouse_locations_name
        ON dbo.warehouse_locations(name);
END;
GO

IF COL_LENGTH('dbo.warehouses', 'location_id') IS NULL
BEGIN
    ALTER TABLE dbo.warehouses
        ADD location_id INT NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_warehouses_warehouse_locations_location_id'
)
BEGIN
    ALTER TABLE dbo.warehouses
        ADD CONSTRAINT FK_warehouses_warehouse_locations_location_id
        FOREIGN KEY (location_id)
        REFERENCES dbo.warehouse_locations(warehouse_location_id);
END;
GO

INSERT INTO dbo.warehouse_locations (name, is_active)
SELECT DISTINCT LTRIM(RTRIM(location)), 1
FROM dbo.warehouses
WHERE location IS NOT NULL
  AND LTRIM(RTRIM(location)) <> ''
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.warehouse_locations wl
      WHERE wl.name = LTRIM(RTRIM(dbo.warehouses.location))
  );
GO

UPDATE w
SET location_id = wl.warehouse_location_id
FROM dbo.warehouses w
INNER JOIN dbo.warehouse_locations wl
    ON wl.name = LTRIM(RTRIM(w.location))
WHERE w.location_id IS NULL
  AND w.location IS NOT NULL
  AND LTRIM(RTRIM(w.location)) <> '';
GO
