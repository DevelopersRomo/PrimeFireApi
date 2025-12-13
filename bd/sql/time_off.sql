-- Time off domain schema
-- Uses DATETIME2 and TIME to avoid legacy datetime precision issues

USE [PrimeFireCorp];
GO

-- --------------------------
-- Time off request enums (SQL Server: enforced via CHECK constraints)
-- --------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeOffRequests')
BEGIN
    CREATE TABLE [dbo].[TimeOffRequests] (
        [RequestId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeOffRequests PRIMARY KEY,
        [EmployeeId] INT NOT NULL,
        [AbsenceType] VARCHAR(20) NOT NULL,
        [Status] VARCHAR(20) NOT NULL CONSTRAINT DF_TimeOffRequests_Status DEFAULT ('pending'),
        [TimeUnit] VARCHAR(20) NOT NULL,
        [StartDate] VARCHAR(10) NOT NULL,
        [EndDate] VARCHAR(10) NOT NULL,
        [StartTime] VARCHAR(8) NULL,
        [EndTime] VARCHAR(8) NULL,
        [TotalHours] VARCHAR(10) NULL,
        [TotalDays] VARCHAR(10) NOT NULL,
        [Reason] NVARCHAR(MAX) NULL,
        [ReviewedBy] INT NULL,
        [ReviewedAt] VARCHAR(19) NULL,
        [ReviewNotes] NVARCHAR(MAX) NULL,
        [CreatedAt] VARCHAR(19) NOT NULL,
        [UpdatedAt] VARCHAR(19) NOT NULL,
        CONSTRAINT FK_TimeOffRequests_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT FK_TimeOffRequests_ReviewedBy FOREIGN KEY ([ReviewedBy]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT CK_TimeOffRequests_AbsenceType CHECK ([AbsenceType] IN ('vacation', 'personal', 'sick')),
        CONSTRAINT CK_TimeOffRequests_Status CHECK ([Status] IN ('pending', 'approved', 'rejected', 'cancelled')),
        CONSTRAINT CK_TimeOffRequests_TimeUnit CHECK ([TimeUnit] IN ('full_day', 'half_day', 'hours'))
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeOffBalances')
BEGIN
    CREATE TABLE [dbo].[TimeOffBalances] (
        [BalanceId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeOffBalances PRIMARY KEY,
        [EmployeeId] INT NOT NULL,
        [AbsenceType] VARCHAR(20) NOT NULL,
        [Year] INT NOT NULL,
        [EntitledDays] VARCHAR(10) NOT NULL CONSTRAINT DF_TimeOffBalances_EntitledDays DEFAULT ('0.00'),
        [UsedDays] VARCHAR(10) NOT NULL CONSTRAINT DF_TimeOffBalances_UsedDays DEFAULT ('0.00'),
        [PendingDays] VARCHAR(10) NOT NULL CONSTRAINT DF_TimeOffBalances_PendingDays DEFAULT ('0.00'),
        [CarryoverDays] VARCHAR(10) NOT NULL CONSTRAINT DF_TimeOffBalances_CarryoverDays DEFAULT ('0.00'),
        CONSTRAINT FK_TimeOffBalances_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT CK_TimeOffBalances_AbsenceType CHECK ([AbsenceType] IN ('vacation', 'personal', 'sick')),
        CONSTRAINT UQ_TimeOffBalances UNIQUE ([EmployeeId], [AbsenceType], [Year])
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Holidays')
BEGIN
    CREATE TABLE [dbo].[Holidays] (
        [HolidayId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Holidays PRIMARY KEY,
        [Name] NVARCHAR(100) NOT NULL,
        [Date] VARCHAR(10) NOT NULL,
        [Year] INT NOT NULL,
        CONSTRAINT UQ_Holidays_Date UNIQUE ([Date])
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Departments')
BEGIN
    CREATE TABLE [dbo].[Departments] (
        [DepartmentId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Departments PRIMARY KEY,
        [Name] NVARCHAR(100) NOT NULL CONSTRAINT UQ_Departments_Name UNIQUE,
        [Code] NVARCHAR(20) NULL
    );
END
GO
