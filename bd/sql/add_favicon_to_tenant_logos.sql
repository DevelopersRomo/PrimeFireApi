-- Migration: Add FavIcon column to TenantLogos table
IF NOT EXISTS (
    SELECT 1 
    FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.TenantLogos') 
    AND name = 'FavIcon'
)
BEGIN
    ALTER TABLE [dbo].[TenantLogos]
    ADD [FavIcon] NVARCHAR(500) NULL;
END
GO
