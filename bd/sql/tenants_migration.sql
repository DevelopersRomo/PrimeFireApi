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
    TenantId INT NOT NULL,
    EmployeeId INT NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Pending', -- Pending, Active, Rejected
    IsDefault BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT FK_TenantEmployees_Tenants FOREIGN KEY (TenantId) REFERENCES Tenants(TenantId),
    CONSTRAINT FK_TenantEmployees_Employees FOREIGN KEY (EmployeeId) REFERENCES Employees(EmployeeId)
);

