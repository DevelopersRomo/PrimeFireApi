-- Migration: Replace tenant_logos.path with theme-specific logo_dark / logo_light
-- Run against the MAIN database (the one backing get_main_db).

-- 1. Add both columns as NULL so existing rows survive the ALTER.
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tenant_logos')
    AND name = 'logo_dark'
)
BEGIN
    ALTER TABLE [dbo].[tenant_logos]
    ADD [logo_dark] VARCHAR(500) NULL;
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tenant_logos')
    AND name = 'logo_light'
)
BEGIN
    ALTER TABLE [dbo].[tenant_logos]
    ADD [logo_light] VARCHAR(500) NULL;
END
GO

-- 2. Carry the current logo into both themes. Developer's Romo keeps one asset
--    for dark and light, and any tenant not handled below keeps its old logo.
UPDATE [dbo].[tenant_logos]
SET [logo_dark] = [path],
    [logo_light] = [path]
WHERE [logo_dark] IS NULL
   OR [logo_light] IS NULL;
GO

-- 3. PrimeFire gets its new per-theme assets.
UPDATE [dbo].[tenant_logos]
SET [logo_dark] = 'assets/primefire/logo-dark.webp',
    [logo_light] = 'assets/primefire/logo-light.webp'
WHERE [tenant_id] = 2;
GO

-- 4. Lock both columns down to match the SQLModel definition.
ALTER TABLE [dbo].[tenant_logos]
ALTER COLUMN [logo_dark] VARCHAR(500) NOT NULL;
GO

ALTER TABLE [dbo].[tenant_logos]
ALTER COLUMN [logo_light] VARCHAR(500) NOT NULL;
GO

-- 5. Drop the superseded column.
IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tenant_logos')
    AND name = 'path'
)
BEGIN
    ALTER TABLE [dbo].[tenant_logos]
    DROP COLUMN [path];
END
GO
