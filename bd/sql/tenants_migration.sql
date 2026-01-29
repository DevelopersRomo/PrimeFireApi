CREATE TABLE Tenants (
    TenantId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    DbConnectionKey NVARCHAR(50) NOT NULL, -- Maps to env var suffix (e.g. "CLIENT_A")
    Description NVARCHAR(255),
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE TenantEmployees (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(100) NULL,
    PasswordHash NVARCHAR(255) NULL,
    TenantId INT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_TenantEmployees_Tenants FOREIGN KEY (TenantId) REFERENCES Tenants(TenantId)
);

