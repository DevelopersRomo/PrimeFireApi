-- Migration: Add Url column to TenantLogos table
-- This column allows public access to logo configuration via URL identifier

-- Step 1: Add Url column if it doesn't exist
IF NOT EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.TenantLogos') 
    AND name = 'Url'
)
BEGIN
    ALTER TABLE [dbo].[TenantLogos]
    ADD [Url] NVARCHAR(500) NULL
END
GO

-- Step 2: Update existing rows with a default URL based on TenantId
-- You may want to customize this based on your needs
IF EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.TenantLogos') 
    AND name = 'Url'
)
BEGIN
    UPDATE [dbo].[TenantLogos]
    SET [Url] = 'tenant-' + CAST(TenantId AS NVARCHAR(10))
    WHERE [Url] IS NULL
END
GO

-- Step 3: Make Url NOT NULL after updating existing rows
IF EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.TenantLogos') 
    AND name = 'Url'
    AND is_nullable = 1
)
BEGIN
    ALTER TABLE [dbo].[TenantLogos]
    ALTER COLUMN [Url] NVARCHAR(500) NOT NULL
END
GO

-- Step 4: Create unique index on Url if it doesn't exist
IF NOT EXISTS (
    SELECT 1 
    FROM sys.indexes 
    WHERE object_id = OBJECT_ID('dbo.TenantLogos') 
    AND name = 'IX_TenantLogos_Url'
)
BEGIN
    CREATE UNIQUE INDEX IX_TenantLogos_Url ON [dbo].[TenantLogos](Url)
END
GO

