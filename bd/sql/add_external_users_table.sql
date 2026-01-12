-- Tabla ligera en BD Principal solo para autenticación de usuarios externos
CREATE TABLE [dbo].[ExternalUsers] (
    ExternalUserId INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    TenantId INT NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_ExternalUsers_Tenants FOREIGN KEY (TenantId) REFERENCES Tenants(TenantId)
);
GO

