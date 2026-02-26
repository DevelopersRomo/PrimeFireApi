-- TimeSheet domain schema
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeSheetPunches')
BEGIN
    CREATE TABLE [dbo].[TimeSheetPunches] (
        [PunchId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeSheetPunches PRIMARY KEY,
        [EmployeeId] INT NOT NULL,
        [CustomerId] INT NOT NULL,
        [ClockInAt] VARCHAR(19) NOT NULL,
        [ClockOutAt] VARCHAR(19) NULL,
        [Timezone] VARCHAR(80) NULL,
        [IpAddress] VARCHAR(45) NULL,
        [Latitude] VARCHAR(20) NULL,
        [Longitude] VARCHAR(20) NULL,
        [GpsAccuracy] VARCHAR(20) NULL,
        [City] NVARCHAR(100) NULL,
        [Region] NVARCHAR(100) NULL,
        [Country] NVARCHAR(100) NULL,
        [LocationRaw] NVARCHAR(MAX) NULL,
        [WorkedMinutes] INT NOT NULL CONSTRAINT DF_TimeSheetPunches_WorkedMinutes DEFAULT (0),
        [Status] VARCHAR(20) NOT NULL CONSTRAINT DF_TimeSheetPunches_Status DEFAULT ('open'),
        [Note] NVARCHAR(MAX) NULL,
        [ApprovedBy] INT NULL,
        [ApprovedAt] VARCHAR(19) NULL,
        [CreatedAt] VARCHAR(19) NOT NULL,
        [UpdatedAt] VARCHAR(19) NOT NULL,
        CONSTRAINT FK_TimeSheetPunches_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT FK_TimeSheetPunches_Customer FOREIGN KEY ([CustomerId]) REFERENCES [dbo].[Customers]([CustomerId]),
        CONSTRAINT FK_TimeSheetPunches_ApprovedBy FOREIGN KEY ([ApprovedBy]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT CK_TimeSheetPunches_Status CHECK ([Status] IN ('open', 'closed', 'approved', 'rejected'))
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeSheetLocationSnapshots')
BEGIN
    CREATE TABLE [dbo].[TimeSheetLocationSnapshots] (
        [SnapshotId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeSheetLocationSnapshots PRIMARY KEY,
        [EmployeeId] INT NOT NULL,
        [CustomerId] INT NULL,
        [IpAddress] VARCHAR(45) NULL,
        [Latitude] VARCHAR(20) NULL,
        [Longitude] VARCHAR(20) NULL,
        [GpsAccuracy] VARCHAR(20) NULL,
        [City] NVARCHAR(100) NULL,
        [Region] NVARCHAR(100) NULL,
        [Country] NVARCHAR(100) NULL,
        [Timezone] VARCHAR(80) NULL,
        [LocationRaw] NVARCHAR(MAX) NULL,
        [CapturedAt] VARCHAR(19) NOT NULL,
        CONSTRAINT FK_TimeSheetLocationSnapshots_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId]),
        CONSTRAINT FK_TimeSheetLocationSnapshots_Customer FOREIGN KEY ([CustomerId]) REFERENCES [dbo].[Customers]([CustomerId])
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TimeSheetSettings')
BEGIN
    CREATE TABLE [dbo].[TimeSheetSettings] (
        [SettingId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeSheetSettings PRIMARY KEY,
        [OvertimeDailyHours] VARCHAR(10) NOT NULL CONSTRAINT DF_TimeSheetSettings_OvertimeDailyHours DEFAULT ('8.00'),
        [OvertimeWeeklyHours] VARCHAR(10) NULL CONSTRAINT DF_TimeSheetSettings_OvertimeWeeklyHours DEFAULT ('40.00'),
        [RoundToMinutes] INT NULL,
        [IsActive] BIT NOT NULL CONSTRAINT DF_TimeSheetSettings_IsActive DEFAULT (1),
        [CreatedAt] VARCHAR(19) NOT NULL,
        [UpdatedAt] VARCHAR(19) NOT NULL
    );
END
GO
