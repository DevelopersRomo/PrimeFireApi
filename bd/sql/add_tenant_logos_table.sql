-- Migration: Add TenantLogos table
-- This table stores logo configurations for tenants

CREATE TABLE [dbo].[TenantLogos] (
    [LogoId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [TenantId] INT NOT NULL,
    [Title] NVARCHAR(100) NOT NULL,
    [Description] NVARCHAR(500) NULL,
    [Path] NVARCHAR(500) NOT NULL,
    [Url] NVARCHAR(500) NOT NULL UNIQUE,
    [PathBackground] NVARCHAR(500) NULL,
    [PrimaryColor] NVARCHAR(50) NULL,
    [SecondaryColor] NVARCHAR(50) NULL,
    [TertiaryColor] NVARCHAR(50) NULL,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [UpdatedAt] DATETIME2 NULL,
    CONSTRAINT FK_TenantLogos_Tenants FOREIGN KEY (TenantId) REFERENCES [dbo].[Tenants](TenantId)
)
GO

CREATE INDEX IX_TenantLogos_TenantId ON [dbo].[TenantLogos](TenantId)
GO

CREATE UNIQUE INDEX IX_TenantLogos_Url ON [dbo].[TenantLogos](Url)
GO

