-- Run against the PrimeFire employee database.
IF OBJECT_ID(N'dbo.employee_m365_archives', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.employee_m365_archives (
        employee_id INT NOT NULL PRIMARY KEY REFERENCES dbo.employees(employee_id)
    );
END;
