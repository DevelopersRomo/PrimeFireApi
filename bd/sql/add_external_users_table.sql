-- Add external user fields to TenantEmployees and drop ExternalUsers
IF COL_LENGTH('dbo.TenantEmployees', 'Email') IS NULL
    ALTER TABLE dbo.TenantEmployees ADD Email NVARCHAR(100) NULL;

IF COL_LENGTH('dbo.TenantEmployees', 'PasswordHash') IS NULL
    ALTER TABLE dbo.TenantEmployees ADD PasswordHash NVARCHAR(255) NULL;

IF COL_LENGTH('dbo.TenantEmployees', 'CreatedAt') IS NULL
    ALTER TABLE dbo.TenantEmployees ADD CreatedAt DATETIME2 NULL;

IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'TenantEmployees'
           AND COLUMN_NAME = 'TenantId' AND IS_NULLABLE = 'NO')
    ALTER TABLE dbo.TenantEmployees ALTER COLUMN TenantId INT NULL;

IF COL_LENGTH('dbo.TenantEmployees', 'EmployeeId') IS NOT NULL
    ALTER TABLE dbo.TenantEmployees DROP COLUMN EmployeeId;

IF COL_LENGTH('dbo.TenantEmployees', 'Status') IS NOT NULL
    ALTER TABLE dbo.TenantEmployees DROP COLUMN Status;

IF COL_LENGTH('dbo.TenantEmployees', 'IsDefault') IS NOT NULL
    ALTER TABLE dbo.TenantEmployees DROP COLUMN IsDefault;

IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE name = 'IX_TenantEmployees_Email'
               AND object_id = OBJECT_ID('dbo.TenantEmployees'))
    CREATE UNIQUE INDEX IX_TenantEmployees_Email
    ON dbo.TenantEmployees (Email) WHERE Email IS NOT NULL;

IF OBJECT_ID('dbo.ExternalUsers', 'U') IS NOT NULL
    DROP TABLE dbo.ExternalUsers;
GO

