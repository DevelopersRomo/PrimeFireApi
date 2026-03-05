IF COL_LENGTH('dbo.Employees', 'Manager') IS NULL
BEGIN
    ALTER TABLE dbo.Employees ADD Manager NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('dbo.Employees', 'ManagerEmail') IS NULL
BEGIN
    ALTER TABLE dbo.Employees ADD ManagerEmail NVARCHAR(100) NULL;
END
GO

IF COL_LENGTH('dbo.Employees', 'ManagerEmployeeId') IS NULL
BEGIN
    ALTER TABLE dbo.Employees ADD ManagerEmployeeId INT NULL;
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_Employees_ManagerEmployee'
      AND parent_object_id = OBJECT_ID('dbo.Employees')
)
BEGIN
    ALTER TABLE dbo.Employees
    WITH CHECK ADD CONSTRAINT FK_Employees_ManagerEmployee
    FOREIGN KEY (ManagerEmployeeId) REFERENCES dbo.Employees(EmployeeId);
END
GO
