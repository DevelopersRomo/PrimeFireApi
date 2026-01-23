USE [PrimeFireCorp]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-01-13 17:56:54 ******/
/****** This script contains ALL table structures and ALL data ******/

-- =============================================
-- DROP ALL TABLES
-- =============================================

IF OBJECT_ID('dbo.TimeOffRequests', 'U') IS NOT NULL
    DROP TABLE dbo.TimeOffRequests;
GO

IF OBJECT_ID('dbo.TimeOffBalances', 'U') IS NOT NULL
    DROP TABLE dbo.TimeOffBalances;
GO

IF OBJECT_ID('dbo.Tickets', 'U') IS NOT NULL
    DROP TABLE dbo.Tickets;
GO

IF OBJECT_ID('dbo.ticketMessages', 'U') IS NOT NULL
    DROP TABLE dbo.ticketMessages;
GO

IF OBJECT_ID('dbo.ticketAttachments', 'U') IS NOT NULL
    DROP TABLE dbo.ticketAttachments;
GO

IF OBJECT_ID('dbo.Tenants', 'U') IS NOT NULL
    DROP TABLE dbo.Tenants;
GO

IF OBJECT_ID('dbo.TenantLogos', 'U') IS NOT NULL
    DROP TABLE dbo.TenantLogos;
GO

IF OBJECT_ID('dbo.TenantEmployees', 'U') IS NOT NULL
    DROP TABLE dbo.TenantEmployees;
GO

IF OBJECT_ID('dbo.Roles', 'U') IS NOT NULL
    DROP TABLE dbo.Roles;
GO

IF OBJECT_ID('dbo.RoleModules', 'U') IS NOT NULL
    DROP TABLE dbo.RoleModules;
GO

IF OBJECT_ID('dbo.Modules', 'U') IS NOT NULL
    DROP TABLE dbo.Modules;
GO

IF OBJECT_ID('dbo.Licenses', 'U') IS NOT NULL
    DROP TABLE dbo.Licenses;
GO

IF OBJECT_ID('dbo.Jobs', 'U') IS NOT NULL
    DROP TABLE dbo.Jobs;
GO

IF OBJECT_ID('dbo.Holidays', 'U') IS NOT NULL
    DROP TABLE dbo.Holidays;
GO

IF OBJECT_ID('dbo.HardwareInventory', 'U') IS NOT NULL
    DROP TABLE dbo.HardwareInventory;
GO

IF OBJECT_ID('dbo.ExternalUsers', 'U') IS NOT NULL
    DROP TABLE dbo.ExternalUsers;
GO

IF OBJECT_ID('dbo.Employees', 'U') IS NOT NULL
    DROP TABLE dbo.Employees;
GO

IF OBJECT_ID('dbo.EmployeeRoles', 'U') IS NOT NULL
    DROP TABLE dbo.EmployeeRoles;
GO

IF OBJECT_ID('dbo.Departments', 'U') IS NOT NULL
    DROP TABLE dbo.Departments;
GO

IF OBJECT_ID('dbo.Curriculums', 'U') IS NOT NULL
    DROP TABLE dbo.Curriculums;
GO

IF OBJECT_ID('dbo.Countries', 'U') IS NOT NULL
    DROP TABLE dbo.Countries;
GO


-- =============================================
-- CREATE ALL TABLES
-- =============================================

-- =============================================
-- Table: Countries
-- =============================================

CREATE TABLE [dbo].[Countries](
    [CountryId] [int] IDENTITY(1,1) NOT NULL,
    [Name] [varchar](20) NULL,
 CONSTRAINT [PK__Countrie__10D1609F78E422F4] PRIMARY KEY CLUSTERED
(
    [CountryId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Curriculums
-- =============================================

CREATE TABLE [dbo].[Curriculums](
    [CurriculumId] [int] IDENTITY(1,1) NOT NULL,
    [JobId] [int] NOT NULL,
    [Name] [varchar](100) NOT NULL,
    [Email] [varchar](100) NOT NULL,
    [Phone] [varchar](20) NULL,
    [CurriculumPath] [varchar](255) NULL,
    [CoverLetter] [varchar](1000) NULL,
    [Status] [varchar](20) NOT NULL,
    [SubmittedAt] [datetime] NOT NULL,
    [EmployeeId] [int] NULL,
 CONSTRAINT [PK__Curricul__06C9FA1C1A1B5187] PRIMARY KEY CLUSTERED
(
    [CurriculumId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Departments
-- =============================================

CREATE TABLE [dbo].[Departments](
    [DepartmentId] [int] IDENTITY(1,1) NOT NULL,
    [Name] [nvarchar](100) NOT NULL,
    [Code] [nvarchar](20) NULL,
 CONSTRAINT [PK_Departments] PRIMARY KEY CLUSTERED
(
    [DepartmentId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: EmployeeRoles
-- =============================================

CREATE TABLE [dbo].[EmployeeRoles](
    [EmployeeId] [int] NOT NULL,
    [RoleId] [int] NOT NULL,
 CONSTRAINT [PK__Employee__C27FE3F0C0F63C02] PRIMARY KEY CLUSTERED
(
    [EmployeeId] ASC,[RoleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Employees
-- =============================================

CREATE TABLE [dbo].[Employees](
    [EmployeeId] [int] IDENTITY(1,1) NOT NULL,
    [FirstName] [varchar](50) NULL,
    [LastName] [varchar](50) NULL,
    [DisplayName] [varchar](100) NULL,
    [Title] [varchar](50) NULL,
    [Department] [varchar](50) NULL,
    [Office] [varchar](50) NULL,
    [Email] [varchar](50) NULL,
    [Phone] [varchar](20) NULL,
    [MobilePhone] [varchar](20) NULL,
    [OfficePhone] [varchar](20) NULL,
    [StreetAddress] [varchar](100) NULL,
    [City] [varchar](50) NULL,
    [State] [varchar](50) NULL,
    [PostalCode] [varchar](20) NULL,
    [CountryId] [int] NULL,
    [AzureOid] [varchar](100) NULL,
    [AzureUpn] [varchar](100) NULL,
    [LastSyncedAt] [datetime] NULL,
    [Anydesk] [nvarchar](50) NULL,
    [PasswordHash] [nvarchar](255) NULL,
    [Manager] [nvarchar](100) NULL,
    [ManagerEmail] [nvarchar](100) NULL,
 CONSTRAINT [PK__Employee__7AD04F1160241B26] PRIMARY KEY CLUSTERED
(
    [EmployeeId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: ExternalUsers
-- =============================================

CREATE TABLE [dbo].[ExternalUsers](
    [ExternalUserId] [int] IDENTITY(1,1) NOT NULL,
    [Email] [varchar](100) NOT NULL,
    [PasswordHash] [varchar](255) NOT NULL,
    [TenantId] [int] NOT NULL,
    [CreatedAt] [datetime] NOT NULL,
 CONSTRAINT [PK__External__94CC235758F0BDBE] PRIMARY KEY CLUSTERED
(
    [ExternalUserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: HardwareInventory
-- =============================================

CREATE TABLE [dbo].[HardwareInventory](
    [HardwareID] [int] IDENTITY(1,1) NOT NULL,
    [SerialNumber] [varchar](50) NOT NULL,
    [Brand] [varchar](50) NOT NULL,
    [Model] [varchar](100) NULL,
    [DeviceType] [varchar](20) NULL,
    [Processor] [varchar](100) NULL,
    [RAM_GB] [int] NULL,
    [StorageType] [varchar](20) NULL,
    [StorageSize_GB] [int] NULL,
    [GPU] [varchar](100) NULL,
    [OperatingSystem] [varchar](100) NULL,
    [WarrantyStartDate] [date] NULL,
    [WarrantyEndDate] [date] NULL,
    [PurchaseDate] [date] NULL,
    [EmployeeId] [int] NULL,
    [Location] [varchar](100) NULL,
    [Status] [varchar](20) NULL,
    [Notes] [varchar](255) NULL,
    [CreatedAt] [datetime] NULL,
    [UpdatedAt] [datetime] NULL,
 CONSTRAINT [PK__Hardware__13A9B58868586958] PRIMARY KEY CLUSTERED
(
    [HardwareID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Holidays
-- =============================================

CREATE TABLE [dbo].[Holidays](
    [HolidayId] [int] IDENTITY(1,1) NOT NULL,
    [Name] [nvarchar](100) NOT NULL,
    [Date] [varchar](10) NOT NULL,
    [Year] [int] NOT NULL,
 CONSTRAINT [PK_Holidays] PRIMARY KEY CLUSTERED
(
    [HolidayId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Jobs
-- =============================================

CREATE TABLE [dbo].[Jobs](
    [JobId] [int] IDENTITY(1,1) NOT NULL,
    [Title] [varchar](100) NOT NULL,
    [Description] [varchar](1000) NULL,
    [Requirements] [varchar](1000) NULL,
    [Location] [varchar](100) NULL,
    [SalaryMin] [float] NULL,
    [SalaryMax] [float] NULL,
    [Status] [varchar](20) NOT NULL,
    [PostedAt] [datetime] NOT NULL,
    [EmployeeId] [int] NULL,
    [CountryId] [int] NULL,
 CONSTRAINT [PK__Jobs__056690C2C3A32B63] PRIMARY KEY CLUSTERED
(
    [JobId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Licenses
-- =============================================

CREATE TABLE [dbo].[Licenses](
    [LicenseId] [int] IDENTITY(1,1) NOT NULL,
    [Software] [varchar](50) NULL,
    [Version] [varchar](20) NULL,
    [CreatedAt] [date] NULL,
    [ExpiryDate] [date] NULL,
    [Key] [varchar](50) NULL,
    [Account] [varchar](50) NULL,
    [Password] [varchar](50) NULL,
    [EmployeeId] [int] NULL,
 CONSTRAINT [PK__Licenses__72D6008283025401] PRIMARY KEY CLUSTERED
(
    [LicenseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Modules
-- =============================================

CREATE TABLE [dbo].[Modules](
    [ModuleId] [int] IDENTITY(1,1) NOT NULL,
    [ModuleName] [varchar](50) NOT NULL,
    [ModuleKey] [varchar](50) NOT NULL,
    [Description] [varchar](200) NULL,
    [Icon] [varchar](50) NULL,
    [RouteUrl] [varchar](100) NULL,
    [DisplayOrder] [int] NULL,
    [IsActive] [bit] NOT NULL,
    [ParentModuleId] [int] NULL,
    [CreatedAt] [datetime] NULL,
 CONSTRAINT [PK__Modules__2B7477A770A3BB13] PRIMARY KEY CLUSTERED
(
    [ModuleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: RoleModules
-- =============================================

CREATE TABLE [dbo].[RoleModules](
    [RoleId] [int] NOT NULL,
    [ModuleId] [int] NOT NULL,
    [CanView] [bit] NOT NULL,
    [CanCreate] [bit] NOT NULL,
    [CanEdit] [bit] NOT NULL,
    [CanDelete] [bit] NOT NULL,
    [CanExport] [bit] NOT NULL,
    [AdminActions] [bit] NOT NULL,
    [OtherActions] [bit] NOT NULL,
    [AssignedAt] [datetime] NULL,
 CONSTRAINT [PK__RoleModu__E84D89600A5756DE] PRIMARY KEY CLUSTERED
(
    [RoleId] ASC,[ModuleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Roles
-- =============================================

CREATE TABLE [dbo].[Roles](
    [RoleId] [int] IDENTITY(1,1) NOT NULL,
    [RoleName] [varchar](50) NOT NULL,
    [Description] [varchar](200) NULL,
 CONSTRAINT [PK__Roles__8AFACE1A81A168C1] PRIMARY KEY CLUSTERED
(
    [RoleId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TenantEmployees
-- =============================================

CREATE TABLE [dbo].[TenantEmployees](
    [Id] [int] IDENTITY(1,1) NOT NULL,
    [TenantId] [int] NOT NULL,
    [EmployeeId] [int] NOT NULL,
    [Status] [varchar](20) NOT NULL,
    [IsDefault] [bit] NOT NULL,
    [CreatedAt] [datetime] NOT NULL,
 CONSTRAINT [PK__TenantEm__3214EC072433EAFD] PRIMARY KEY CLUSTERED
(
    [Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TenantLogos
-- =============================================

CREATE TABLE [dbo].[TenantLogos](
    [LogoId] [int] IDENTITY(1,1) NOT NULL,
    [TenantId] [int] NOT NULL,
    [Title] [varchar](100) NOT NULL,
    [Description] [varchar](500) NULL,
    [Path] [varchar](500) NOT NULL,
    [PathBackground] [varchar](500) NULL,
    [PrimaryColor] [varchar](50) NULL,
    [SecondaryColor] [varchar](50) NULL,
    [TertiaryColor] [varchar](50) NULL,
    [CreatedAt] [datetime] NOT NULL,
    [UpdatedAt] [datetime] NULL,
    [Url] [nvarchar](500) NOT NULL,
 CONSTRAINT [PK__TenantLo__C620158D40BFCF43] PRIMARY KEY CLUSTERED
(
    [LogoId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Tenants
-- =============================================

CREATE TABLE [dbo].[Tenants](
    [TenantId] [int] IDENTITY(1,1) NOT NULL,
    [Name] [varchar](100) NOT NULL,
    [DbConnectionKey] [varchar](50) NOT NULL,
    [Description] [varchar](255) NULL,
    [IsActive] [bit] NOT NULL,
    [CreatedAt] [datetime] NOT NULL,
 CONSTRAINT [PK__Tenants__2E9B47E1F92EB300] PRIMARY KEY CLUSTERED
(
    [TenantId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: ticketAttachments
-- =============================================

CREATE TABLE [dbo].[ticketAttachments](
    [TicketAttachmentId] [int] IDENTITY(1,1) NOT NULL,
    [TicketId] [int] NOT NULL,
    [TicketMessageId] [int] NULL,
    [FileName] [varchar](255) NOT NULL,
    [FileType] [varchar](100) NULL,
    [FilePath] [varchar](500) NULL,
    [CreatedAt] [datetime] NOT NULL,
 CONSTRAINT [PK__ticketAt__25528BC8235CC48C] PRIMARY KEY CLUSTERED
(
    [TicketAttachmentId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: ticketMessages
-- =============================================

CREATE TABLE [dbo].[ticketMessages](
    [TicketMessageId] [int] IDENTITY(1,1) NOT NULL,
    [TicketId] [int] NOT NULL,
    [UserId] [int] NOT NULL,
    [MessageTxt] [varchar](MAX) NULL,
    [CreatedAt] [datetime] NOT NULL,
    [UpdatedAt] [datetime] NULL,
    [EditedAt] [datetime] NULL,
 CONSTRAINT [PK__ticketMe__602A18A4D77F2994] PRIMARY KEY CLUSTERED
(
    [TicketMessageId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Tickets
-- =============================================

CREATE TABLE [dbo].[Tickets](
    [TicketId] [int] IDENTITY(1,1) NOT NULL,
    [Title] [varchar](200) NOT NULL,
    [Description] [varchar](2000) NULL,
    [Status] [varchar](11) NOT NULL,
    [Priority] [varchar](6) NOT NULL,
    [SLA] [varchar](3) NULL,
    [CreatedBy] [int] NOT NULL,
    [AssignedTo] [int] NULL,
    [CreatedAt] [datetime] NOT NULL,
    [UpdatedAt] [datetime] NOT NULL,
 CONSTRAINT [PK__Tickets__712CC607ABD622AB] PRIMARY KEY CLUSTERED
(
    [TicketId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TimeOffBalances
-- =============================================

CREATE TABLE [dbo].[TimeOffBalances](
    [BalanceId] [int] IDENTITY(1,1) NOT NULL,
    [EmployeeId] [int] NOT NULL,
    [AbsenceType] [varchar](20) NOT NULL,
    [Year] [int] NOT NULL,
    [EntitledDays] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [UsedDays] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [PendingDays] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [CarryoverDays] [varchar](10) NOT NULL DEFAULT ('0.00'),
 CONSTRAINT [PK_TimeOffBalances] PRIMARY KEY CLUSTERED
(
    [BalanceId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TimeOffRequests
-- =============================================

CREATE TABLE [dbo].[TimeOffRequests](
    [RequestId] [int] IDENTITY(1,1) NOT NULL,
    [EmployeeId] [int] NOT NULL,
    [AbsenceType] [varchar](20) NOT NULL,
    [Status] [varchar](20) NOT NULL DEFAULT ('pending'),
    [TimeUnit] [varchar](20) NOT NULL,
    [StartDate] [varchar](10) NOT NULL,
    [EndDate] [varchar](10) NOT NULL,
    [StartTime] [varchar](8) NULL,
    [EndTime] [varchar](8) NULL,
    [TotalHours] [varchar](10) NULL,
    [TotalDays] [varchar](10) NOT NULL,
    [Reason] [nvarchar](MAX) NULL,
    [ReviewedBy] [int] NULL,
    [ReviewedAt] [varchar](19) NULL,
    [ReviewNotes] [nvarchar](MAX) NULL,
    [CreatedAt] [varchar](19) NOT NULL,
    [UpdatedAt] [varchar](19) NOT NULL,
 CONSTRAINT [PK_TimeOffRequests] PRIMARY KEY CLUSTERED
(
    [RequestId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


-- =============================================
-- INSERT DATA FOR ALL TABLES
-- =============================================


-- Data for Countries (5 records)
SET IDENTITY_INSERT [dbo].[Countries] ON
GO

INSERT [dbo].[Countries] ([CountryId], [Name]) VALUES (1, N'US')
INSERT [dbo].[Countries] ([CountryId], [Name]) VALUES (2, N'PR')
INSERT [dbo].[Countries] ([CountryId], [Name]) VALUES (3, N'DO')
INSERT [dbo].[Countries] ([CountryId], [Name]) VALUES (4, N'MX')
INSERT [dbo].[Countries] ([CountryId], [Name]) VALUES (5, N'Mexico')

SET IDENTITY_INSERT [dbo].[Countries] OFF
GO


-- Curriculums: No data to insert


-- Departments: No data to insert


-- Data for Employees (47 records)
SET IDENTITY_INSERT [dbo].[Employees] ON
GO

INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (1, N'Admin', N'Guaynabo', N'Admin Guaynabo', NULL, NULL, NULL, N'Administration@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'8eeb508a-9f43-41ec-80dc-36a63c0aea48', N'Administration@primefire.us', '2026-01-13 04:47:18', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (2, N'Adolfo', N'Martinez', N'Adolfo Martinez', N'Manager Alarm Designer', N'Engineering Alarms', N'Home Office TX', N'amartinez@primefire.us', NULL, N'+1 4075584334', N'+1 4075584334', N'Dallas, TX', N'Dallas', N'Texas (TX)', N'75202', 1, N'1e7152f1-aaf5-4789-9da4-e74d9b586843', N'amartinez@primefire.us', '2025-11-06 18:15:59', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (3, N'Jose Alberto', N'Rodriguez', N'Jose Alberto Rodriguez', N'President & CEO', N'President', N'Trujillo Alto, Puerto Rico', N'arodriguez@primefire.us', NULL, N'+1 7872212121', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b826abb3-30c8-4369-8d87-ce0d648e7fba', N'arodriguez@primefire.us', '2025-11-06 18:15:59', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (4, N'Baxter', N'Jayuya', N'Baxter Jayuya', N'Engineering Alarm', N'Engineering Alarm Designer', N'Guaynabo, Puerto Rico', N'bjayuya@primefire.us', NULL, NULL, N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'b9de2f69-4aba-42f3-87eb-da0e1dcf2cfa', N'bjayuya@primefire.us', '2025-11-06 18:16:00', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (5, N'Christopher', N'Carballo Rosado', N'Christopher Carballo Rosado', N'Fire Alarm Manager', N'Alarm Project Manager', N'Guaynabo, Puerto Rico', N'ccarballo@primefire.us', NULL, N'+1 7872017346', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'd63e397b-31e7-424e-a2c3-993562347b04', N'ccarballo@primefire.us', '2025-11-06 18:16:00', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (6, N'Cesar', N'Figueroa Cruzado', N'Cesar Figueroa Cruzado', N'Group Leader', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'cfigueroa@primefire.us', NULL, N'+1 9398919203 ', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', NULL, N'b5ff98b3-be60-4693-aa6e-2553b941faff', N'cfigueroa@primefire.us', '2026-01-13 04:47:20', NULL, NULL, N'Santiago Rodriguez', N'srodriguez@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (7, N'Jose Daniel', N'Agosto Rivera', N'Jose Daniel Agosto Rivera', NULL, NULL, NULL, N'dagosto@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'a5c57db5-230b-41c2-a0e7-0747f4512d2d', N'dagosto@primefire.us', '2026-01-13 04:47:20', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (8, NULL, NULL, N'Dominicana', NULL, NULL, NULL, N'dominicana@primefire.do', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'405c6850-50aa-490a-91f0-b666e016f12e', N'dominicana@primefire.do', '2026-01-13 04:47:20', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (9, N'Edwin', N'De Jesus', N'Edwin De Jesus', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'edejesus@primefire.us', NULL, N'+1 7876433660', N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1efe087c-1bd7-4e77-9ec3-5577519a9871', N'edejesus@primefire.us', '2025-11-06 18:16:01', NULL, NULL, N'Edwin De Jesus', N'edejesus@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (10, N'Emmanuel', N'Desueza', N'Enmanuel Desueza', N'Project Coordinator', N'Field Technician, Office Assistant ', N'Santo Domingo, República Dominicana', N'edesueza@primefire.do', NULL, N'+1 8095011901', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'b0241d3b-03a7-45bf-a2fa-f06a76b9317d', N'edesueza@primefire.do', '2025-11-06 18:16:02', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (11, N'Edwin', N'Guilloty', N'Edwin Guilloty', N'Project Manager', N'Operations', N'Guaynabo, Puerto Rico', N'eguilloty@primefire.us', NULL, N'+1 7876433660', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'76025b90-b5a8-4ba7-809b-0da6685492f8', N'eguilloty@primefire.us', '2025-11-06 18:16:03', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (12, N'Elizaud', N'Hernandez', N'Elizaud Hernandez', N'Administration Manager', N'Administration', N'Trujillo Alto, Puerto Rico', N'ehernandez@primefire.us', NULL, N'+1 3867483621', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'ad15e516-906b-4e3f-8e4c-373134505755', N'ehernandez@primefire.us', '2025-11-06 18:16:03', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (13, N'Emilio', N'Melendez', N'Emilio Melendez', N'Field Tech', N'Logistics / Operations', N'Prime Fire DO', N'emelendez@primefire.do', NULL, NULL, NULL, N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominiaca', N'10109', 3, N'4c12442f-758b-4921-8188-b0167d3e6281', N'emelendez@primefire.do', '2025-11-06 18:16:03', NULL, NULL, N'Enmanuel Desueza', N'edesueza@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (14, N'Elionetzy', N'Santiago Adames', N'Elionetzy Santiago Adames', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto', N'esadames@primefire.us', NULL, N'+1 7874729866', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b892a33-b52b-4f24-9af1-941c3eceb183', N'esadames@primefire.us', '2025-11-06 18:16:04', NULL, NULL, N'Edwin Guilloty', N'eguilloty@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (15, N'Gustavo', N'Heredia', N'Gustavo Heredia', N'Designer ', NULL, NULL, N'gheredia@primefire.do', NULL, N'+1 8492854334', NULL, N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'44d8c9a2-c02f-41c7-85e0-50c9f92ec327', N'gheredia@primefire.do', '2025-11-06 18:16:04', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (16, N'Geurys Jabbart', N'Medrano Montero', N'Geurys Medrano', N'Global Inventory Manager', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'gmedrano@primefire.do', NULL, N'+1 8295594355', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6dc58092-0b27-431c-a2b6-353e2fcf4c49', N'gmedrano@primefire.do', '2025-11-06 18:16:05', NULL, NULL, N'Enmanuel Desueza', N'edesueza@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (17, N'Gustavo', N'Vazquez', N'Gustavo Vazquez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvazquez@primefire.us', NULL, N'1 (787) 312-7679', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'07e0c48e-bc49-4f58-9e3b-c391b4fe12c2', N'gvazquez@primefire.us', '2025-11-06 18:16:05', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (18, N'Giovanni', N'Velez', N'Giovanni Velez', N'Fire Alarm Project Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvelez@primefire.us', NULL, N'+1 7873700568', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8b6db431-ee49-46c2-be9a-2e89a493130a', N'gvelez@primefire.us', '2025-11-06 18:16:05', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (19, NULL, NULL, N'Info', NULL, NULL, NULL, N'info@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'53172d9b-ad7e-49e4-81ce-25c1c7656a3e', N'info@primefire.us', '2026-01-13 04:47:22', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (20, N'Israel', N'Nieves', N'Israel Nieves', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto, Puerto Rico', N'inieves@primefire.us', NULL, N'+1 7872047807', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'396751cd-b9ac-40e9-8122-dffb9341f319', N'inieves@primefire.us', '2025-11-06 18:16:06', NULL, NULL, N'Edwin Guilloty', N'eguilloty@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (21, N'Jonathan', N'Romo', N'Jonathan Romo', N'Admin Systems', N'IT', N'Home Office, Mexico', N'it@primefire.us', NULL, N'+528125356287', N'+528125356287', N'Arturo B de la Garza #4613', N'Monterrey', NULL, NULL, 4, N'8c882f2c-19f8-4f17-a1e8-d5644456ea65', N'it@primefire.us', '2025-11-06 18:16:07', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (22, N'Juan', N'Aybar', N'Juan Lehtenin', N'Fire Alarm Division', N'PrimeFire DO', N'República Dominica', N'jaybar@primefire.do', NULL, NULL, N'+1 8095011901', N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominicana', N'10109', 3, N'2a9640a5-897f-49c0-94f7-15a6f4d642c9', N'jaybar@primefire.do', '2025-11-06 18:16:07', NULL, NULL, N'Santiago Rodriguez', N'srodriguez@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (23, N'Joskayra', N'de Jesus Medina', N'Joskayra de Jesus Medina', N'Engineering Alarm Designer & Accountant', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'jdejesus@primefire.do', NULL, N'+1 809-499-5821', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'df97493e-56d4-45fb-8a18-25a60dead4b5', N'jdejesus@primefire.do', '2025-11-06 18:16:08', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (24, N'Javier', N'Lopez Rivera', N'Javier Lopez Rivera', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jlopez@primefire.us', NULL, N'+1 9393399185', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'e809702b-2fb2-45d3-b486-04f66b89d725', N'jlopez@primefire.us', '2025-11-06 18:16:08', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (25, N'Jose', N'Martínez', N'Jose Martínez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jmartinez@primefire.us', NULL, N'+1 787-948-3352', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1eb06cab-eeae-425b-bd0e-562d6eb89735', N'jmartinez@primefire.us', '2025-11-06 18:16:08', NULL, NULL, N'Edwin De Jesus', N'edejesus@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (26, N'Jose', N'Morales', N'Jose Morales', N'Group Leader', N'Sprinklers Division', N'Trujillo Alto, Puerto Rico', N'jmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'd96be71d-b61f-40e5-b973-94843acf7c47', N'jmorales@primefire.us', '2025-11-06 18:16:09', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (27, N'Juan', N'Villa', N'Juan Villa', N'Systems', N'IT', N'Home Office, Mexico', N'jvilla@primefire.us', N'1231231232', N'+522282553841', N'+522282553841', N'Retorno Pantochica #3', N'Xalapa', N'Veracruz', N'91098', 4, N'0523631c-d286-4be5-9aaf-e33ac83b587c', N'jvilla@primefire.us', '2025-12-27 23:43:06', N'1231231232', NULL, N'Jonathan Romo', N'it@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (28, N'Kevin', N'Morales', N'Kevin Morales', N'Administrative Assistant', N'HR Analyst', N'Trujillo Alto, Puerto Rico', N'kmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b7ae779-a20d-47d9-9680-ccf54568ae41', N'kmorales@primefire.us', '2025-11-06 18:16:10', NULL, NULL, N'Sigfredo Carrero', N'scarrero@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (29, N'Kristian', N'Torres', N'Kristian Torres', N'Field Tech', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ktorres@primefire.us', NULL, N'+1 4077059670', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'b02a129b-cb1f-4d22-ab12-acbbeb5291e2', N'ktorres@primefire.us', '2025-11-06 18:16:10', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (30, N'Luis', N'Burset', N'Luis Burset', N'Fire Sprinklers Designer', N'Designer', N'Home Office TX', N'lburset@primefire.us', NULL, N'+1 7874855008', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR', N'00976', 2, N'88b8d661-148d-4476-881c-d42f4d3ef96e', N'lburset@primefire.us', '2025-11-06 18:16:10', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (31, N'Luis', N'De Jesus', N'Luis De Jesus', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ldejesus@primefire.us', NULL, N'+1 7873909755', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8d91aafe-6b6d-4994-84d4-5108e4e7b0ca', N'ldejesus@primefire.us', '2025-11-06 18:16:11', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (32, N'Luis', N'Nieves', N'Luis Nieves', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'lnieves@primefire.us', NULL, N'+1 7873641643', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'8f082fd0-cad1-4579-8305-08b31f95befd', N'lnieves@primefire.us', '2025-11-06 18:16:11', NULL, NULL, N'Sigfredo Carrero', N'scarrero@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (33, N'Max', N'Oliveras', N'Max Oliveras', N'Project Manager', N'Field Engineering', N'Trujillo Alto', N'moliveras@primefire.us', NULL, N'+ 787 607 7402', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'41b65f97-f746-46c2-b03a-9f0dffaefb19', N'moliveras@primefire.us', '2025-11-06 18:16:12', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (34, N'Marcos', N'Quiles', N'Marcos Quiles', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'mquiles@primefire.us', NULL, N'+1 7875257965', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'0f46165b-1617-4d70-82f4-f4768b01f90c', N'mquiles@primefire.us', '2025-11-06 18:16:12', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (35, N'Nathan', N'Gonzalez', N'Nathan Gonzalez', N'Engineering Alarm Designers', N'Engineering Alarm', N'Trujillo Alto, Puerto Rico', N'ngonzalez@primefire.us', NULL, N'+1 7879819444', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'c9d2250f-2b79-403f-9c13-fe11212f4ebb', N'ngonzalez@primefire.us', '2025-11-06 18:16:13', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (36, NULL, NULL, N'Printer Guaynabo', NULL, NULL, NULL, N'Printer-Guaynabo@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'5719f4d2-8092-48f8-a53a-d6f0e28bf8ea', N'Printer-Guaynabo@primefire.us', '2026-01-13 04:47:24', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (37, N'Rayneé', N'Fúnez Heredia', N'Rayneé Fúnez Heredia', N'Account Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'rfunez@primefire.us', NULL, N'+1 9392350216', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'ab01cd10-bff4-4620-b55e-0d0f1ab1d151', N'rfunez@primefire.us', '2025-11-06 18:16:13', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (38, N'Rolando', N'Rivera', N'Rolando Rivera', N'Alarm Designer', NULL, N'Guaynabo, Puerto Rico', N'rrivera@primefire.us', NULL, N'+1 7872377217', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'706337f9-ef71-47cb-982f-2ca206383da3', N'rrivera@primefire.us', '2025-11-06 18:16:14', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (39, N'Sigfredo', N'Carrero', N'Sigfredo Carrero', N'General Manager / Sprinkler Division', N'SubDirection', N'Trujillo Alto, Puerto Rico', N'scarrero@primefire.us', NULL, N'+1 7876475955', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b7d6932d-8c4c-411f-ab87-1547f9c07391', N'scarrero@primefire.us', '2025-11-06 18:16:14', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (40, NULL, NULL, N'service', NULL, NULL, NULL, N'service@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'f1228614-b6eb-4c3e-bbae-869139b6736e', N'service@primefire.us', '2026-01-13 04:47:24', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (41, N'Stephanie', N'Martinez', N'Stephanie Martinez', N'HR Analyst', N'Hiuman Resource', N'Trujillo Alto, Puerto Rico', N'smartinez@primefire.us', NULL, N'+1 8292485211', N'+1 8095011901', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'9cfcf921-1266-468c-a7de-0ee20fd472cb', N'smartinez@primefire.us', '2025-11-06 18:16:15', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (42, N'Santiago', N'Rodriguez', N'Santiago Rodriguez', N'Operation Manager', N'Field Engineering ', N'Santo Domingo, República Dominicana', N'srodriguez@primefire.do', NULL, N'+1 7876077402', N'+1 7877613180', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'635af9c2-ca37-4e5a-bfdd-989e0f7d14a9', N'srodriguez@primefire.do', '2025-11-06 18:16:15', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (43, N'Willian', N'Bencosme', N'Willian Bencosme', N'Engineering Alarm & FireSpronkler', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'wbencosme@primefire.do', NULL, N'+1 8297653844', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6987d8c8-0423-43bb-be3e-6601476147ab', N'wbencosme@primefire.do', '2025-11-06 18:16:16', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (44, N'Wilnelia', N'Santos', N'Wilnelia Santos', N'HR Analyst', N'Hiuman Resource', N'Republica Dominicana', N'wsantos@primefire.us', NULL, N'+1 7877613180', N'+1 8608413625', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'be4788a5-f480-442d-ab40-209e317e54ac', N'wsantos@primefire.us', '2025-12-22 18:25:48', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (45, N'Luis', N'Belliard', N'Luis Belliard', N'Fire Sprinklers Designer', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'lbelliard@primefire.do', NULL, N'+1 8292222869', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6e029e87-b520-4def-8aed-9484162bee13', N'lbelliard@primefire.do', '2025-11-13 18:05:51', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do')
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (46, N'Kevin', N'Lopez', N'Kevin Lopez', NULL, NULL, NULL, N'klopez@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'ac51c4f9-269a-44a8-99b9-aae4220a7e4e', N'klopez@primefire.us', '2026-01-13 04:47:23', NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail]) VALUES (47, N'Juan', N'Villa', N'Juan Villa', N'External User', NULL, NULL, N'jcarlos.villa.rivera@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'$2b$12$fiPTctfjmqCHlsIKwhYdGeTCs3f8WyZIrJfgTaFHM0mLKtCjqr1BW', NULL, NULL)

SET IDENTITY_INSERT [dbo].[Employees] OFF
GO


-- Data for Roles (5 records)
SET IDENTITY_INSERT [dbo].[Roles] ON
GO

INSERT [dbo].[Roles] ([RoleId], [RoleName], [Description]) VALUES (1, N'Admin', N'System Administrator with full access')
INSERT [dbo].[Roles] ([RoleId], [RoleName], [Description]) VALUES (2, N'Manager', N'Department manager with elevated permissions')
INSERT [dbo].[Roles] ([RoleId], [RoleName], [Description]) VALUES (3, N'User', N'Standard user with basic access')
INSERT [dbo].[Roles] ([RoleId], [RoleName], [Description]) VALUES (5, N'Jobs ', N'Administrador modulo Jobs')
INSERT [dbo].[Roles] ([RoleId], [RoleName], [Description]) VALUES (8, N'Admin_Tenants', N'Tenants')

SET IDENTITY_INSERT [dbo].[Roles] OFF
GO


-- Data for EmployeeRoles (57 records)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (1, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (2, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (2, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (3, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (4, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (5, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (5, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (6, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (7, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (8, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (9, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (10, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (10, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (11, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (11, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (12, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (13, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (14, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (15, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (16, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (17, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (18, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (18, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (19, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (20, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (21, 1)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (21, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (22, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (23, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (24, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (25, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (26, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (27, 1)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (27, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (27, 8)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (28, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (29, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (30, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (31, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (32, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (33, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (33, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (34, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (35, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (36, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (37, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (38, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (39, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (39, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (40, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (41, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (42, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (43, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (44, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (44, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (45, 3)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (46, 3)
GO


-- Data for Tenants (3 records)
SET IDENTITY_INSERT [dbo].[Tenants] ON
GO

INSERT [dbo].[Tenants] ([TenantId], [Name], [DbConnectionKey], [Description], [IsActive], [CreatedAt]) VALUES (1, N'CLIENTE_A', N'CLIENTE_A', N'Created via user registration', 0, '2025-12-21 20:11:39')
INSERT [dbo].[Tenants] ([TenantId], [Name], [DbConnectionKey], [Description], [IsActive], [CreatedAt]) VALUES (2, N'Pending Approval', N'PENDING', N'Placeholder for users pending tenant assignment', 0, '2025-12-21 21:55:47')
INSERT [dbo].[Tenants] ([TenantId], [Name], [DbConnectionKey], [Description], [IsActive], [CreatedAt]) VALUES (3, N'DEVROMO', N'DEVROMO', N'Developers Romo', 1, '2026-01-12 00:00:00')

SET IDENTITY_INSERT [dbo].[Tenants] OFF
GO


-- Data for ExternalUsers (6 records)
SET IDENTITY_INSERT [dbo].[ExternalUsers] ON
GO

INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (2, N'jcarlos.villa.rivera@gmail.com', N'$2b$12$jDA.P0tv/HoVGX3Z6pRESOKj3TZgpdIHNsfkgWL4wGdKjN2u.2kBS', 1, '2025-12-21 21:31:20')
INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (3, N'test@test.com', N'$2b$12$Bw7RTrbud0DkIaITWZsEfujMXh2dR6y4T51wb5SWjP2wvkPhNPWAu', 1, '2025-12-21 21:55:48')
INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (4, N'pepe@test.com', N'$2b$12$vrIZoXv/CLip.iWaHPldO.wq0wRxb/JVhcz25.Fu0hZ5EkL6uOxtC', 1, '2025-12-23 17:09:33')
INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (5, N'doe@test.com', N'$2b$12$kxEdN6WNnqqJXD4u47hQgOeV3Oobe4f5KRWch.7slSIMCr7CHhFt.', 1, '2025-12-27 23:30:18')
INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (6, N'lucas@lucas.com', N'$2b$12$geVBjNyC.ZAI4O8jFfohoekYoQeBF37RTyi95xMemG3p7VgAQ5QJu', 1, '2025-12-27 23:32:43')
INSERT [dbo].[ExternalUsers] ([ExternalUserId], [Email], [PasswordHash], [TenantId], [CreatedAt]) VALUES (7, N'pepito@pe.com', N'$2b$12$Thqdtv3QWsbIftk3tTXHV.KlURhSeGm8NknQXNNFXE5H7jOPH2GCy', 2, '2025-12-29 11:02:39')

SET IDENTITY_INSERT [dbo].[ExternalUsers] OFF
GO


-- Data for HardwareInventory (22 records)
SET IDENTITY_INSERT [dbo].[HardwareInventory] ON
GO

INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (5, N'405QCSF568390', N'LG', N'LG PC', N'Laptop', N'Intel(R) Core(TM) Ultra 7 155H (1.4 GHz)', NULL, N'SSD', 1000, NULL, N'Windows 11 Pro', '2025-01-01', '2025-01-01', '2025-01-01', 46, N'Trujillo  Alto', N'Active', N'Computadora de Kevin Lopez', '2025-11-17 22:13:57', '2025-11-25 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (6, N'601-7E07-030B2212003338', N'MILLENIUM', N'MILLENIUM', N'Laptop', N'13th Gen Intel(R) Core(TM)  i9-13900K (3.00 GHz)', NULL, N'SSD', 4000, NULL, N'Windows 11 Pro', '2024-01-01', '2026-01-01', '2024-01-01', 45, N'Republica Dominicana', N'Active', N'es maquina de Luis Belliard', '2025-11-19 22:45:00', '2025-11-25 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (7, N'6CSMVN0', N'MS-7D07', N'MS-7D07', N'Desktop', N'Intel(R) Core(TM) i9-10850K CPU @ 3.60Ghz  ( 3.60Ghz)', NULL, N'SSD', 464, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-31', 35, N'Guaynabo PR', N'Active', N'Esta com putadora es una maquina armada ', '2025-11-25 14:37:51', '2025-11-25 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (8, N'55F9HTU', N'MS-7E06', N'MS-7E06', N'Desktop', N'Intel iCore I9-14900K(3.20 Ghz)', NULL, N'SSD', 8000, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-31', 23, N'Republica Dominicana', N'Active', N'Maquina Armada', '2025-11-26 00:21:51', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (9, N'KVBN8DJ', N'Z490 UD AC-Y1', N'Z490 UD AC-Y1', N'Desktop', N'Intel(R) Core-i7 10700K', NULL, N'SSD', 1375, NULL, N'Windows 10 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 19, N'Republica Dominicana', N'Active', N'Maquina on Hold desktop (diseño) en Republica Dominicana. Compuitadora Armada
', '2025-11-28 16:38:03', '2025-12-20 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (10, N'5CD243JJ42', N'HP', N'Pavilion Laptop 15', N'Laptop', N'12th Gen Intel(R) Core(TM) i7-1255U', NULL, N'SSD', 475, NULL, N'Windows 11 Pro', '2025-12-01', '2025-12-01', '2025-12-01', 16, N'Republica Dominicana', N'Active', N'Laptop de Geurys ', '2025-12-04 21:21:40', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (12, N'2MO4271TGM', N'HP', N'ENVY TE TE01', N'Laptop', N'Intel(R) Core(TM) i5-14400 (2.50 GHz)', NULL, N'SSD', 466, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 28, N'Trujillo Alto', N'Active', N'', '2025-12-08 15:30:11', '2025-12-22 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (13, N'PF5Z0QV1', N'Lenovo', N'Legión 5 16IAX10', N'Laptop', N'Intel(R) Core(TM) Ultra 9 275HX (2.7 GHz)', NULL, N'SSD', 951, NULL, N'Windows 11 Pro', '2025-12-12', '2026-12-14', '2025-12-14', 43, N'República Dominicana ', N'Active', N'Laptop compartida William y Joskayra', '2025-12-16 14:39:23', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (14, N'0027234201758', N'DSK', N'Corsair Vengeance', N'Desktop', N'13th Gen Intel(R) Core(TM) i9-13900K (3.00 GHz)', NULL, N'SSD', 1820, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 2, N'Orlando, Florida', N'Active', N'Maquina desktop de Adolfo', '2025-12-22 13:53:29', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (15, N'et8259-2152', N'CiberPowerPC', N'Gaming PC ', N'Desktop', N'Intel(R) Core(TM) Ultra 9 285K (3.7 GHz)', NULL, N'SSD', 1810, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 38, N'Guaynabo', N'Active', N'Máquina de Escritorio ', '2025-12-22 14:14:36', '2025-12-22 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (16, N'7FJBYS3', N'DELL', N'Inspirion 3910', N'Laptop', N'12th Gen Intel(R) Core(TM) i5-12400 (2.50 Ghz)', NULL, N'SSD', 1140, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-01', 44, N'Guaynabo', N'Active', N'Laptop de Wilnelia', '2025-12-22 17:55:58', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (17, N'0F34MHY25013HJ', N'Micrsosoft Surface', N'7 Edition', N'Laptop', N'Snapdragon(R) X 12-core X1E80100 @ 3.40 GHz (3.42 GHz)', NULL, N'NVMe', 954, NULL, N'Windows 11 Pro', '2025-06-01', '2026-06-01', '2025-06-01', 12, N'Trujillo Alto', N'Active', N'Laptop de Elizaud', '2025-12-23 14:01:15', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (19, N'NA ', N'NA - Pending', N'NA - Pending ', N'Desktop', N'Intel(R) Core (TM) i5-8400 CPU @ 2.800Ghz ', NULL, N'HDD', 224, NULL, N'Windows 10 Pro', '2023-01-01', '2024-01-01', '2023-01-01', 12, N'Trujillo Alto', N'Active', N'Desktop de Elizaud 
Pc de Gabinete pero no viene Marca, Serial Ni Modelo', '2025-12-23 14:24:58', '2025-12-23 00:00:00')
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (20, N'TL0PHNT', N'Micro-Star International', N'MS-7C08', N'Desktop', N'Intel(R) Core (TM) i3-8100 CPU @ 3.6 Ghz', NULL, N'SSD', 224, NULL, N'Windows 10 Pro', '2023-01-01', '2024-01-01', '2023-01-01', 11, N'Trujillo ', N'Active', N'Maquina desktop de Edwin', '2025-12-23 15:36:51', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (21, N'T5PFAG00N805214', N'Asus', N'ROG G700TF', N'Desktop', N'Intel(R) Core (TM)', NULL, N'SSD', 1860, NULL, N'Windows 11 Pro', '2025-05-13', '2026-05-13', '2025-05-13', 43, N'Republica Dominicana', N'Active', N'Desktop de Willian ', '2025-12-23 18:32:54', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (22, N'ET8226-1657', N'GamingPC', N'GamingPC', N'Desktop', N'AMD Ryzen 9 7900X 12-Core Processor (4.70 GHz)', NULL, N'SSD', 1820, NULL, N'Windows 11 Pro', '2025-02-24', '2026-02-24', '2025-02-24', 32, N'Trujillo Alto', N'Active', N'Maquina desktop Luis Nieves ', '2025-12-23 20:21:22', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (23, N'408QCUK573870', N'LG', N'PC', N'Laptop', N'Intel(R) Core(TM) Ultra 7 155H (1.4 Ghz)', NULL, N'SSD', 954, NULL, N'Windiws 11 Pro', '2023-11-12', '2024-11-12', '2023-11-12', 24, N'Guaynabo', N'Active', N'Laptop en uso', '2025-12-29 16:36:46', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (24, N'Default', N'MS-7D91', N'MS-7D91', N'Desktop', N'13Th Intel (R) Core(TM) i9-13900k (3.00 Ghz)', NULL, N'SSD', 2730, NULL, N'Windows 11 Pro', '2024-08-13', '2025-08-13', '2024-08-13', 34, N'Trujillo Alto', N'Active', N'Computadora de Marcos Quiles', '2025-12-29 17:55:40', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (25, N'DQM57J2', N'Dell', N'Optiplex 3040', N'Laptop', N'Intel(R) Core(TM) i5 6500-T CPU @ 2.50 GHz', NULL, N'SSD', 477, NULL, N'Windows 11 Pro', '2022-04-02', '2023-04-04', '2022-04-04', 29, N'Guaynabo', N'Active', N'Laptop de Kristian', '2025-12-29 18:52:27', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (26, N'PW03wJET', N'Lenovo ', N'Flex 7 14IAU7', N'Laptop', N'Intel Core I7-125U', NULL, N'SSD', 477, NULL, N'Windows 11 Pro', '2024-02-02', '2025-02-02', '2024-02-02', 8, N'República Dominicana ', N'Active', N'Laptop Alessa ', '2026-01-06 13:38:17', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (27, N'B660M-HDV', N'NA', N'B660M-HDV', N'Desktop', N'Intel ICore 3 13th 3.4 Ghz', NULL, N'SSD', 477, NULL, N'Windows 10 Pro', '2016-03-15', '2017-03-15', '2016-03-15', 39, N'Trujillo Alto', N'Active', N'Computadora Desktop de Sigfredo no aparece el Service Tag', '2026-01-09 15:10:15', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (29, N'NXJDJAA00150405F6D7600', N'Acer', N'Laptop Acer NXJK7AA002 14 pulgadas', N'Laptop', N'Intel(R) Core(TM) Ultra 5 226V (2.10 GHz)', NULL, N'SSD', 1000, NULL, N'Windows 11 Pro', '2025-01-01', '2026-01-01', '2025-01-01', 6, N'Trujillo Alto', N'Active', N'', '2026-01-12 16:45:31', NULL)

SET IDENTITY_INSERT [dbo].[HardwareInventory] OFF
GO


-- Holidays: No data to insert


-- Jobs: No data to insert


-- Data for Licenses (60 records)
SET IDENTITY_INSERT [dbo].[Licenses] ON
GO

INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (2, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 8)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (3, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (4, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (5, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (6, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (7, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 35)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (8, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (9, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (10, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 2)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (11, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'YY8HR-MRN7Y-GJQ22-VTYYB-PR4D9', N'NA', N'NA', 32)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (13, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'RN964-Y9TP4-C9XB3-R7JCY-F9CMK', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (14, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'6C3H9-NF4XV-M7B9T-2FKMJ-Q69VX', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (15, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'NBRB7-DXRTG-78F3J-6DH6H-X767X', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (16, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'6YPF7-NVQTX-CFRFY-K8H8K-V22MK', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (17, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'PTNYH-C3K4Y-R2V4Y-FVK7G-KTPMK', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (18, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'JW2N2-VY84G-7B4WQ-F8TRG-TJGBK', N'NA', N'NA', 43)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (19, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'X3NXY-WQF6G-6TYHP-VGMR4-JHV39', N'NA', N'NA', 16)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (20, N'Project Professional', N'2016', '2025-01-01', '2030-12-31', N'NA', N'.exe', N'NA', 33)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (22, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (23, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'KNBXT-476VY-4MD7F-WD96T-3V66T', N'NA', N'NA', 12)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (24, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'QV29N-MB22V-W77GF-V7YWD-9D726', N'NA', N'NA', 10)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (25, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'GQ632-4NHC2-874P6-WY9F3-C3726', N'NA', N'NA', 16)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (26, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'KKNY3-6G7QC-9MV22-B8FKG-H8RC6', N'NA', N'NA', 24)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (27, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'BMHN4-RV8TH-384JX-MRBQW-F3KTT', N'NA', N'NA', 3)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (28, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'JJD6F-GN9FY-Q8GR3-T6TYQ-YBH26', N'NA', N'NA', 42)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (29, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'NDQPV-Q8C4R-6DG4R-RP7JR-369TT', N'NA', N'NA', 33)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (30, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N' 7TNMC-WG9JC-FXW9P-JTYYM-QJ3GT', N'NA', N'NA', 5)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (31, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'XKKX3-N9D4Q-F2MHB-TW9VF-PPQGT', N'NA', N'NA', 41)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (32, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WN9QH-23YXT-JFJG2-GYJBY-K766T', N'NA', N'NA', 38)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (33, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WBQHR-NYK2T-RTXF7-9XYDR-JHV26', N'NA', N'NA', 43)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (34, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (35, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (36, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'NWFKH-V99CG-MV63M-PGQYD-7T9TT', N'NA', N'NA', 3)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (37, N'Windows 11 Pro', N'2025', '2025-12-09', '2030-12-31', N'HM2F6-NTVVH-V4YWB-7BC2M-39MP6', N'NA', N'NA', 17)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (38, N'Windows11 Pro', N'2025', '2025-12-01', '2026-12-01', N'WTNHY-BR399-MBF4T-7HHQW-VH66T', N'NA', N'NA', 3)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (39, N'Revit', N'2025', '2025-11-30', '2026-11-30', N'575-04949370', N'NA', N'NA', 23)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (40, N'Revit', N'2025', '2025-11-30', '2026-11-29', N'575-04949370', N'NA', N'NA', 43)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (41, N'Revit', N'2025', '2025-12-17', '2026-12-16', N'574-73837017', N'NA', N'NA', 23)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (42, N'Adobe Acrobat', N'2020 Standart', '2025-12-10', '2026-12-15', N'118-1981-0736-3346-2793-4534', N'NA', N'NA', 17)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (43, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 12)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (44, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 10)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (45, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1714-6444-4243-6737-2511', N'NA', N'NA', 12)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (46, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1714-6444-4243-6737-2511', N'NA', N'NA', 3)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (47, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 25)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (48, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 25)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (49, N'AlarmCAD', N'2023', '2025-02-28', '2026-02-28', N'EGBC4-CJLTC-64K8C- FA9BX-6NXUJ-9', N'Amartinez@primefire.us', N'', 2)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (50, N'AutoSPRINK Platinum', N'2024', '2024-12-31', '2025-12-31', N'9WVCN-X5X63-3TYME-GMTYJ-NMJP4-4', N'lbusert@primefire.us', N'Na', 30)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (51, N'AutoSPRINK Lite', N'2024', '2025-02-04', '2026-02-04', N'ZFHG6-JYC26-X2K9A-UWQN5-9A8VK-6', N'Lnieves@primefire.us', N'NA', 32)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (52, N'AutoSPRINK Lite', N'2024', '2025-02-04', '2026-02-04', N'ZFHG6-JYC26-X2K9A-UWQN5-9A8VK-6', N'Lbilleard@primefire.us', N'NA', 45)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (53, N'AlarmCAD ', N'2023', '2024-05-31', '2025-05-31', N'7HPVU-ZS2L3-Q8YA9-ZZHC7-26PPB-2 ', N'Jmedina@primefire.us', N'NA', 23)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (54, N'AlarmCAD', N'2023', '2024-03-03', '2025-03-03', N'ARFQH-LQ9N5-JMRJB-QR5NJ-C58FT-4', N'Wbencosme@primefire.us', N'NA', 43)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (55, N'AutoCAD', N'Full Version', '2025-06-06', '2026-06-06', N'NA', N'amartinez@primefire.us', N'NA', 2)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (56, N'AutoCAD', N'Full Version', '2025-03-20', '2026-03-03', N'NA', N'lnieves@primefire.us', N'NA', 32)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (57, N'AutoCAD', N'FullVersion', '2025-06-10', '2026-06-10', N'NA', N'lburset@primefire.us', N'NA', 30)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (58, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'', N'NA', N'NA', 19)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (59, N'AutoCAD', N'Full Version', '2025-06-03', '2026-06-03', N'NA', N'ngonzalwz@primefire.us', N'NA', 35)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (60, N'AutoCAD ', N'LT', '2025-11-29', '2026-11-29', N'Na', N'Sofia Rodriguez', N'NA', 3)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (67, N'AutoCAD', N'AutoCAD 2025', '2025-11-27', '2026-11-27', N'574-62827022', N'NA', N' A', 23)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (68, N'AutoCAD ', N'Full Version ', '2025-06-10', '2026-06-10', N'NA', N'Arodriguez@promefire.us', N'NA', 34)
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId]) VALUES (69, N'ZenFire', N'Subscription CRM', '2026-01-05', '2027-01-05', N'Subscription', N'ALL ', N'NA', 21)

SET IDENTITY_INSERT [dbo].[Licenses] OFF
GO


-- Data for Modules (12 records)
SET IDENTITY_INSERT [dbo].[Modules] ON
GO

INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard and analytics', N'dashboard', N'/dashboard', 1, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (3, N'Jobs', N'jobs', N'Job postings management', N'work', N'/jobs', 2, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (5, N'Licenses', N'licenses', N'Software licenses management', N'vpn_key', N'/licenses', 5, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (6, N'Administration', N'administration', N'System administration', N'settings', N'/config', 6, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'config/permissions/roles', 6, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (8, N'Permissions', N'permissions', N'Module permissions management', N'lock', N'/config/permissions', 9, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (10, N'Modules', N'modules', N'modules', N'Modules', N'/config/permissions/modules', 7, 1, 6, '2025-10-18 22:40:51')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (11, N'Employees', N'employees', N'Employees Module', N'People', N'/employees', 2, 1, NULL, '2025-10-19 17:31:12')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (12, N'Tickets', N'tickets', N'', N'', N'/tickets', 10, 1, NULL, '2025-10-28 02:24:35')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (13, N'Hardware Inventory', N'hardwareInventory', N'Modulo para gestionar inventario de equipos', N'settings', N'/hardware-inventory', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'', N'', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')

SET IDENTITY_INSERT [dbo].[Modules] OFF
GO


-- Data for RoleModules (27 records)
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:10')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 3, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:11')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 5, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:11')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 6, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:11')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 7, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:11')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 8, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:12')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 10, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:12')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 11, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:10')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 12, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:12')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 13, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:13')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 14, 1, 1, 1, 1, 1, 1, 1, '2026-01-08 02:37:10')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 15, 0, 0, 0, 0, 0, 0, 0, '2026-01-08 02:37:09')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (2, 3, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (2, 14, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (3, 12, 1, 1, 1, 1, 1, 0, 0, '2025-12-13 16:58:09')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 1, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 3, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 5, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 6, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 7, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 8, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 10, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 11, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 12, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 13, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 14, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 15, 1, 1, 1, 1, 1, 1, 1, '2025-12-28 05:40:41')
GO


-- TenantEmployees: No data to insert


-- Data for TenantLogos (2 records)
SET IDENTITY_INSERT [dbo].[TenantLogos] ON
GO

INSERT [dbo].[TenantLogos] ([LogoId], [TenantId], [Title], [Description], [Path], [PathBackground], [PrimaryColor], [SecondaryColor], [TertiaryColor], [CreatedAt], [UpdatedAt], [Url]) VALUES (1, 1, N'Cliente A', N'Cliente A', N'assets/Test-Logo.webp', N'assets/test-hero.webp', NULL, NULL, NULL, '2025-12-28 00:14:01', NULL, N'localhost:4201')
INSERT [dbo].[TenantLogos] ([LogoId], [TenantId], [Title], [Description], [Path], [PathBackground], [PrimaryColor], [SecondaryColor], [TertiaryColor], [CreatedAt], [UpdatedAt], [Url]) VALUES (2, 3, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com')

SET IDENTITY_INSERT [dbo].[TenantLogos] OFF
GO


-- Data for Tickets (69 records)
SET IDENTITY_INSERT [dbo].[Tickets] ON
GO

INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (1, N'Deploy App to Azure', N'invest how to deploy the app Python and angular to Azure', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:05:03', '2025-11-25 14:16:36')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (2, N'Anydesk Column', N'Add Anydesk Column to employees Table and show ', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:06:37', '2025-11-25 14:17:05')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (3, N'Iframe Jobs Work4 PrimeFire 2 Sites', N'Add the Frame Jobs(Vacancies) to the new webpages  ', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:08:22', '2025-11-25 14:17:15')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (4, N'Migration webpage Cpanel to Plesk ', N'we need to migrate the cpanel webp app to plesk hosting', N'TODO', N'NORMAL', NULL, 21, 27, '2025-11-20 13:12:49', '2025-11-20 13:12:49')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (5, N'Carpeta Compartida Impresora Canon', N'esta carpeta es necesaria para las impresiones ', N'CLOSED', N'NORMAL', NULL, 21, 21, '2025-11-25 14:26:24', '2025-11-25 14:26:52')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (8, N'Popup Tickets Tema Negro', N'El Popup cuando se muestra se ve en negro', N'CLOSED', N'MEDIUM', NULL, 21, 27, '2025-11-26 00:39:14', '2025-11-29 20:25:14')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (9, N'Filtros Tickets Module', N'En el modulo Tickets debe de empezar con 
Filtro al inicio 
Assigned me
mes actual
activos
Ahi que agregar un filtro extra de rango  de fechas.

Si tengo rol de user solo ver mis tickets activos cerrados y activos. si tengo rol de Manager o admin puedo ver todos los tickets.
La vista siempre debe empezar con activos y asignados a mi. pero debe existir la opcion de guardar la vista en el storage
Entonces ahi que crear un servicio que tenga las credenciales usuario y rol. para determinar las vistas.

validaciones. 
Managers puede crear tickets a todos
Users solo puede crear Tickets a IT.
', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-26 00:49:22', '2025-11-29 20:25:09')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (10, N'Validar campos mandatorios en Jobs ', N'Validación 
•Campos mandatorios en Jobs 
•Cambiar el ejemplo de Mexico City a San Juan City.

', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-26 01:26:25', '2025-11-29 20:25:06')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (11, N'Validación Formulario Tickets ', N'Validación campos mandatorios 
Validación máximo y mínimo de caracteres en Title y descripción
El SLA no debe ser opcional y las opciones son 
1 hora o menos 
4 horas 
8 horas 
48 horas 
1 week 
2 weeks 
1 Month 


', N'CLOSED', N'NORMAL', N'12h', 21, 27, '2025-11-26 01:34:28', '2025-11-29 20:25:02')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (12, N'Validation Licences ', N'Campos mandatorios 
Deshabilitar expired date hasta que se llene create at.
Debe pintarse de la siguiente manera acorde las fechas

Amarillo 3 meses antes de vencer la licencia
Naranja 2 meses antes de vencer la licencia 
Rojo 1 mes antes de vencer la licencia 

Agregar nombre de usuario licencia asignada.
', N'TODO', N'NORMAL', N'1w', 21, 21, '2025-11-26 01:41:40', '2025-12-20 18:06:55')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (16, N'Instalacion de Revit - William', N'Se requiere esta instalacion de software para modelar en 3D ', N'CLOSED', N'URGENT', N'4h', 21, 27, '2025-12-02 17:20:26', '2025-12-09 17:47:27')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (17, N'Instalacion paquete Office, Luis Belliard', N'Necesito el paquete de MS office para poder acceder a los BOM de los proyectos', N'CLOSED', N'NORMAL', N'1w', 45, 21, '2025-12-02 17:40:30', '2025-12-09 17:47:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (18, N'Instalación de REVIT- Joskayra Medina', N'La instalación de este software se require para realizar modelados en 3D, ya se instaló esta mañana por el momento todo va marchando bien.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-02 19:07:06', '2025-12-03 01:15:35')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (19, N'Instalar Software Revit', N'Se requiere la instalación del software revit para el modelado de planos en 3D.', N'CLOSED', N'NORMAL', N'1h', 43, 21, '2025-12-02 19:34:47', '2025-12-03 01:15:43')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (20, N'Licencia de AlarmCAD Reasignar', N'La licencia de AlarmCAD no me funciona, ahí que reasignarla por que aparece que ya esta en uso', N'CLOSED', N'MEDIUM', N'4h', 21, 21, '2025-12-09 17:54:45', '2025-12-09 17:57:38')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (21, N'validacion siempre  To/Do sin ser editable el ticket al momento del create ', N'validacion siempre el "Status" To/Do sin ser editable el ticket al momento del create  ', N'CLOSED', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:32:42', '2025-12-10 02:53:48')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (22, N'Poner los formatos de files que soporta', N'si el modulo de Tickets soporta 
.pdf,.word,excel tipos de imagenes, cuando se suba un documento mostrar "uploaded", al momento de enviar verificar si vuelve a cargar los documentos', N'CLOSED', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:35:31', '2025-12-10 02:47:45')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (23, N'Share Knowledge Submodulos Jobs & Tickets', N'Hacer un documento que explique el como hacer un ticket & como crear un Job ', N'TODO', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:39:40', '2025-12-10 00:39:40')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (25, N'support con equipo', N'se solicito asistencia para poder trabajar los PDF que no e abren ', N'CLOSED', N'NORMAL', N'4h', 46, 21, '2025-12-11 17:41:14', '2025-12-12 13:42:02')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (26, N'CONFIGURACION NUEVA PC', N'INSTALACION DE TODOS LOS PROGRAMAS DE DISEÑO  (AUTOCAD, REVIT, BLUE BEAM, SKETCHUP) PARA NUEVA LAPTOP.', N'CLOSED', N'MEDIUM', N'4h', 43, 21, '2025-12-15 14:08:46', '2025-12-19 02:48:56')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (27, N'Mover los botones de time off a Calendar', N'primero ahi que crear un modulo que se llame administration
dentro ira 
-Calendar
-TimeSheet 

y mover las secciones dentro de la primera pagina Time Off - Calendar
', N'CLOSED', N'NORMAL', N'8h', 21, 27, '2025-12-15 23:18:56', '2025-12-27 23:12:23')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (28, N'Inventory Adolfo', N'Hacer Inventario a maquina de Adolfo', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 23:51:05', '2025-12-22 14:23:22')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (29, N'Inventory Alberto', N'Hacer Inventario a maquina de Alberto', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 16:55:26', '2025-12-15 16:55:26')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (30, N'Inventory Cesar Figueroa Cruzado', N'Hacer Inventario a maquina de Cesar Figueroa Cruzado', N'CLOSED', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-12 16:45:58')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (31, N'Inventory Christopher Carballo Rosado', N'Hacer Inventario a maquina de Christopher Carballo Rosado', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (32, N'Inventory Alessa', N'Hacer Inventario a maquina de Alessa', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2026-01-06 16:49:50')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (33, N'Inventory Edwin de Jesus', N'Hacer Inventario a maquina de Edwin de Jesus', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (34, N'Inventory Edwin Guilloty', N'Hacer Inventario a maquina de Edwin Guilloty', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 15:38:50')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (35, N'Inventory Elionetzi Santiago Adames', N'Hacer Inventario a maquina de Elionetzi Santiago Adames', N'TODO', N'NORMAL', N'2w', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:10:51')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (36, N'Inventory Elizaud Hdz', N'Hacer Inventario a maquina de Elizaud Hdz', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 14:11:51')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (37, N'Inventory Emilio Melendez', N'Hacer Inventario a maquina de Emilio Melendez', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:11:23')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (38, N'Inventory Enmanuel Desueza', N'Hacer Inventario a maquina de Enmanuel Desueza', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (39, N'Inventory Geurys Medrano', N'Hacer Inventario a maquina de Geurys Medrano', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:32:48')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (40, N'Inventory Giovanni Velez', N'Hacer Inventario a maquina de Giovanni Velez', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (41, N'Inventory Gustavo Vazquez', N'Hacer Inventario a maquina de Gustavo Vazquez', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (42, N'Inventory Israel Nieves', N'Hacer Inventario a maquina de Israel Nieves', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:06:32')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (43, N'Inventory Javier Lopez Rivera', N'Hacer Inventario a maquina de Javier Lopez Rivera', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:07:09')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (44, N'Inventory Jose Daniel Agisto Rivera', N'Hacer Inventario a maquina de Jose Daniel Agisto Rivera', N'TODO', N'NORMAL', N'2w', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:07:34')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (45, N'Inventory Jose Martinez', N'Hacer Inventario a maquina de Jose Martinez', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:07:59')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (46, N'Inventory Jose Morales', N'Hacer Inventario a maquina de Jose Morales', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:08:29')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (47, N'Inventory Joskayra de Jesus Medina', N'Hacer Inventario a maquina de Joskayra de Jesus Medina', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:30:30')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (48, N'Inventory Kevin Lopez', N'Hacer Inventario a maquina de Kevin Lopez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 19:34:39')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (49, N'Inventory Kevin Morales', N'Hacer Inventario a maquina de Kevin Morales', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:33:55')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (50, N'Inventory Kristian Torres', N'Hacer Inventario a maquina de Kristian Torres', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-29 19:06:37')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (51, N'Inventory Luis Belliard', N'Hacer Inventario a maquina de Luis Belliard', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:16:59')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (52, N'Inventory Luis Burset', N'Hacer Inventario a maquina de Luis Burset', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (53, N'Inventory Luis De Jesus', N'Hacer Inventario a maquina de Luis De Jesus', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:09:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (54, N'Inventory Luis Nieves', N'Hacer Inventario a maquina de Luis Nieves', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 20:23:30')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (55, N'Inventory Marcos Quiles', N'Hacer Inventario a maquina de Marcos Quiles', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-29 19:24:45')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (56, N'Inventory Max Oliveras', N'Hacer Inventario a maquina de Max Oliveras', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (57, N'Inventory Nathan Gonzalez', N'Hacer Inventario a maquina de Nathan Gonzalez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:34:50')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (58, N'Inventory Rolando Rivera', N'Hacer Inventario a maquina de Rolando Rivera', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 14:24:16')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (59, N'Inventory Santiago Rodriguez', N'Hacer Inventario a maquina de Santiago Rodriguez', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (60, N'Inventory Sigfredo Carrero', N'Hacer Inventario a maquina de Sigfredo Carrero', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (61, N'Inventory Willian Bnecosme', N'Hacer Inventario a maquina de Willian Bnecosme', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:03:03')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (62, N'Inventory Wilnelia Santos', N'Hacer Inventario a maquina de Wilnelia Santos', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 17:56:18')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (63, N'Onedrive', N'Sync error due to not enough space', N'CLOSED', N'NORMAL', N'1h', 2, 21, '2025-12-18 18:22:04', '2025-12-19 02:46:57')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (64, N'Reinstalación de Revit ', N'La aplicación arrojo que la licencia fue caducada por lo cual, se tuvo que reinstalar el software nuevamente.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-18 20:25:26', '2025-12-19 02:46:22')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (65, N'Botón Créate debe ser Flotante ', N'Botón créate debe ser Flotante y solo debe tener acceso el admin module ', N'TODO', N'NORMAL', N'1w', 21, 21, '2025-12-20 18:05:17', '2025-12-20 18:05:17')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (66, N'Mas grises los botones del menú en White ', N'Los títulos de los submodulos no están muy visibles cuando el tema es White ', N'CLOSED', N'MEDIUM', N'2w', 21, 27, '2025-12-20 18:22:25', '2025-12-27 23:11:54')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (67, N'Inventario Nathan Gonzalez', N'Hacer inventario Nathan Gonzalez de su PC', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-20 18:27:16', '2025-12-20 18:29:46')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (68, N'Configuración remota via Anydesk', N'Configuración remota via Anydesk, para trabajar remoto los días lunes 29 y martes 30 de diciembre.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-23 17:52:34', '2025-12-23 18:33:30')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (69, N'Remover configuración de Inicio automático. ', N'Remover configuración de Inicio automático.', N'CLOSED', N'NORMAL', N'1h', 43, 21, '2025-12-23 18:36:14', '2025-12-23 23:18:44')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (70, N'Improvments Licenses ', N'Change color in expire date
disabled expired date & autopopulate expire date when is creating screen then set 1 year 
show the name of the employee', N'CLOSED', N'NORMAL', N'4h', 21, 21, '2025-12-26 22:18:30', '2025-12-26 22:18:41')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (71, N'changes in Hardware inventory', N'change color acording waranty 
autopopulate waranty 
show wmployee in list', N'CLOSED', N'NORMAL', N'4h', 21, 21, '2025-12-26 22:20:40', '2026-01-05 23:14:42')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (76, N'Instalar Office Test', N'Instalar office a Kevin ', N'CLOSED', N'MEDIUM', N'4h', 21, 21, '2025-12-30 17:19:14', '2025-12-30 17:21:18')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (77, N'Push Notifications Via Email', N'-Cuando se Cree un nuevo ticket automaticamente debe llegar un correo al asigned To
-Cuando se cree un comentario debe tomar la decicion de quien esta creando el comentario y a quien va dirigido en este caso solo existe la logica de Created By y asigned to.
-En time off - Calendar el usuario quien esta realizando el ticket debe llegar una notificacion a su manager
', N'CLOSED', N'MEDIUM', N'1w', 21, 27, '2026-01-06 00:04:29', '2026-01-08 03:05:09')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (78, N'Conexion a nueva Base de datos ', N'Voy a migrar la base de datos a sql de azure 
te dejo la conexion 
Driver={ODBC Driver 18 for SQL Server};Server=tcp:server-primefiredb.database.windows.net,1433;Database=primefirebd;Uid=PrimeFire;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;', N'TODO', N'NORMAL', N'1w', 21, 21, '2026-01-06 00:09:00', '2026-01-06 00:09:00')
INSERT [dbo].[Tickets] ([TicketId], [Title], [Description], [Status], [Priority], [SLA], [CreatedBy], [AssignedTo], [CreatedAt], [UpdatedAt]) VALUES (81, N'Acceso Servidor TA', N'Se solicito acceso servidor a TA para poder acceder mas informacion de proyectos mientrsas se completa la migracion a proyectos PFP Server
', N'CLOSED', N'NORMAL', N'1h', 46, 21, '2026-01-08 12:36:53', '2026-01-08 13:52:57')

SET IDENTITY_INSERT [dbo].[Tickets] OFF
GO


-- Data for ticketMessages (19 records)
SET IDENTITY_INSERT [dbo].[ticketMessages] ON
GO

INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (1, 16, 21, N'Ok Willian reviso la compra de la licencia', '2025-12-02 17:22:05', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (2, 20, 21, N'Se mando correo y se esta validando con el equipo de MepCAD', '2025-12-09 17:56:09', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (5, 23, 21, N'test', '2025-12-11 02:28:30', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (6, 27, 21, N'adjunto imagen de los improvmens', '2025-12-15 23:19:27', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (7, 63, 21, N'Se borraron algunos archivos duplicados', '2025-12-19 02:46:53', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (8, 26, 21, N'Se configuró nueva PC para Willian y Joskayra con los programas de Cinstrucciom', '2025-12-19 02:48:52', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (9, 61, 21, N'Se realizó el inventario de Computadora y de la laptop', '2025-12-20 18:02:59', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (10, 51, 21, N'Inventario a su maquina', '2025-12-20 18:16:55', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (11, 39, 21, N'Se realizó inventario a la laptop', '2025-12-20 18:32:43', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (12, 49, 21, N'Se realizó inventario e instalación de licencia', '2025-12-20 18:33:52', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (13, 28, 21, N'Inventario Realizado', '2025-12-22 14:23:19', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (14, 58, 21, N'Inventario Realizado', '2025-12-22 14:23:49', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (16, 76, 21, N'Kevin Necesito una aprovacion de parte de Elizaud', '2025-12-30 17:20:11', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (17, 76, 21, N'imagen', '2025-12-30 17:20:49', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (18, 23, 27, N'test', '2026-01-05 23:44:26', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (19, 77, 27, N'test', '2026-01-08 03:12:24', '2026-01-08 03:25:58', '2026-01-08 03:25:58')
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (20, 81, 21, N'listo concedido Kevin, saludos', '2026-01-08 13:52:26', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (21, 78, 21, N'ya subi la cadena de conexio', '2026-01-10 16:22:30', NULL, NULL)
INSERT [dbo].[ticketMessages] ([TicketMessageId], [TicketId], [UserId], [MessageTxt], [CreatedAt], [UpdatedAt], [EditedAt]) VALUES (22, 78, 21, N'foto hny', '2026-01-10 16:23:12', NULL, NULL)

SET IDENTITY_INSERT [dbo].[ticketMessages] OFF
GO


-- Data for ticketAttachments (4 records)
SET IDENTITY_INSERT [dbo].[ticketAttachments] ON
GO

INSERT [dbo].[ticketAttachments] ([TicketAttachmentId], [TicketId], [TicketMessageId], [FileName], [FileType], [FilePath], [CreatedAt]) VALUES (4, 23, 5, N'angular.png', N'image/png', N'tickets/23/c298fa41042247a1b4bfaa9a53f1492a.png', '2025-12-11 02:28:31')
INSERT [dbo].[ticketAttachments] ([TicketAttachmentId], [TicketId], [TicketMessageId], [FileName], [FileType], [FilePath], [CreatedAt]) VALUES (5, 27, 6, N'VacationsImproves.png', N'image/png', N'tickets/27/0d56d010084d4dd78de4e732c3d4bccd.png', '2025-12-15 23:19:29')
INSERT [dbo].[ticketAttachments] ([TicketAttachmentId], [TicketId], [TicketMessageId], [FileName], [FileType], [FilePath], [CreatedAt]) VALUES (6, 76, 17, N'sumas.jpg', N'image/jpeg', N'tickets/76/f49e6b762cac49f5ad4548465caf0131.jpg', '2025-12-30 17:20:50')
INSERT [dbo].[ticketAttachments] ([TicketAttachmentId], [TicketId], [TicketMessageId], [FileName], [FileType], [FilePath], [CreatedAt]) VALUES (7, 77, 19, N'nfpa-logo-1.png', N'image/png', N'D:/home/uploads/tickets/77/995695a047bd4734bf9a65ceaeb25021.png', '2026-01-08 03:25:59')

SET IDENTITY_INSERT [dbo].[ticketAttachments] OFF
GO


-- Data for TimeOffBalances (4 records)
SET IDENTITY_INSERT [dbo].[TimeOffBalances] ON
GO

INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (1, 27, N'vacation', 2025, N'0', N'2.00', N'0.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (2, 21, N'vacation', 2025, N'0', N'0', N'2.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (3, 21, N'sick', 2025, N'0', N'0', N'2.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (4, 27, N'vacation', 2026, N'0', N'1.00', N'1.00', N'0')

SET IDENTITY_INSERT [dbo].[TimeOffBalances] OFF
GO


-- Data for TimeOffRequests (6 records)
SET IDENTITY_INSERT [dbo].[TimeOffRequests] ON
GO

INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (1, 27, N'vacation', N'approved', N'full_day', N'2025-12-08', N'2025-12-08', NULL, NULL, NULL, N'1.00', N'string', 27, N'2025-12-10 00:57:54', NULL, N'2025-12-08 04:39:42', N'2025-12-10 00:57:54')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (2, 27, N'vacation', N'approved', N'full_day', N'2025-12-12', N'2025-12-12', NULL, NULL, NULL, N'1.00', N'fydfhdfhgfhjfgj', 27, N'2025-12-10 00:57:50', NULL, N'2025-12-08 04:51:53', N'2025-12-10 00:57:50')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (3, 21, N'vacation', N'pending', N'full_day', N'2025-12-22', N'2025-12-23', NULL, NULL, NULL, N'2.00', N'necesito este dia por que tengo un viaje programado', NULL, NULL, NULL, N'2025-12-22 18:06:36', N'2025-12-22 18:06:36')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (4, 21, N'sick', N'pending', N'full_day', N'2025-12-30', N'2025-12-31', NULL, NULL, NULL, N'2.00', N'necesito este permiso para ir al doctor', NULL, NULL, NULL, N'2025-12-30 17:24:21', N'2025-12-30 17:24:21')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (5, 27, N'vacation', N'pending', N'full_day', N'2026-01-08', N'2026-01-08', NULL, NULL, NULL, N'1.00', N'test', NULL, NULL, NULL, N'2026-01-08 02:34:02', N'2026-01-08 02:34:02')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (6, 27, N'vacation', N'approved', N'full_day', N'2026-01-10', N'2026-01-10', NULL, NULL, NULL, N'1.00', NULL, 27, N'2026-01-08 02:37:34', NULL, N'2026-01-08 02:36:03', N'2026-01-08 02:37:34')

SET IDENTITY_INSERT [dbo].[TimeOffRequests] OFF
GO


-- =============================================
-- FOREIGN KEYS
-- =============================================

ALTER TABLE [dbo].[EmployeeRoles] WITH CHECK ADD CONSTRAINT [FK__EmployeeR__Emplo__247D636F]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[EmployeeRoles] CHECK CONSTRAINT [FK__EmployeeR__Emplo__247D636F]
GO

ALTER TABLE [dbo].[EmployeeRoles] WITH CHECK ADD CONSTRAINT [FK__EmployeeR__RoleI__257187A8]
FOREIGN KEY([RoleId])
REFERENCES [dbo].[Roles] ([RoleId])
GO
ALTER TABLE [dbo].[EmployeeRoles] CHECK CONSTRAINT [FK__EmployeeR__RoleI__257187A8]
GO

ALTER TABLE [dbo].[Employees] WITH CHECK ADD CONSTRAINT [FK__Employees__Count__1DD065E0]
FOREIGN KEY([CountryId])
REFERENCES [dbo].[Countries] ([CountryId])
GO
ALTER TABLE [dbo].[Employees] CHECK CONSTRAINT [FK__Employees__Count__1DD065E0]
GO

ALTER TABLE [dbo].[ExternalUsers] WITH CHECK ADD CONSTRAINT [FK__ExternalU__Tenan__08012052]
FOREIGN KEY([TenantId])
REFERENCES [dbo].[Tenants] ([TenantId])
GO
ALTER TABLE [dbo].[ExternalUsers] CHECK CONSTRAINT [FK__ExternalU__Tenan__08012052]
GO

ALTER TABLE [dbo].[HardwareInventory] WITH CHECK ADD CONSTRAINT [FK__HardwareI__Emplo__0E240DFC]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[HardwareInventory] CHECK CONSTRAINT [FK__HardwareI__Emplo__0E240DFC]
GO

ALTER TABLE [dbo].[Jobs] WITH CHECK ADD CONSTRAINT [FK_Jobs_Countries]
FOREIGN KEY([CountryId])
REFERENCES [dbo].[Countries] ([CountryId])
GO
ALTER TABLE [dbo].[Jobs] CHECK CONSTRAINT [FK_Jobs_Countries]
GO

ALTER TABLE [dbo].[Modules] WITH CHECK ADD CONSTRAINT [FK__Modules__ParentM__19FFD4FC]
FOREIGN KEY([ParentModuleId])
REFERENCES [dbo].[Modules] ([ModuleId])
GO
ALTER TABLE [dbo].[Modules] CHECK CONSTRAINT [FK__Modules__ParentM__19FFD4FC]
GO

ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK__RoleModul__RoleI__20ACD28B]
FOREIGN KEY([RoleId])
REFERENCES [dbo].[Roles] ([RoleId])
GO
ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK__RoleModul__RoleI__20ACD28B]
GO

ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK__RoleModul__Modul__21A0F6C4]
FOREIGN KEY([ModuleId])
REFERENCES [dbo].[Modules] ([ModuleId])
GO
ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK__RoleModul__Modul__21A0F6C4]
GO

ALTER TABLE [dbo].[TenantEmployees] WITH CHECK ADD CONSTRAINT [FK__TenantEmp__Tenan__033C6B35]
FOREIGN KEY([TenantId])
REFERENCES [dbo].[Tenants] ([TenantId])
GO
ALTER TABLE [dbo].[TenantEmployees] CHECK CONSTRAINT [FK__TenantEmp__Tenan__033C6B35]
GO

ALTER TABLE [dbo].[TenantEmployees] WITH CHECK ADD CONSTRAINT [FK__TenantEmp__Emplo__04308F6E]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TenantEmployees] CHECK CONSTRAINT [FK__TenantEmp__Emplo__04308F6E]
GO

ALTER TABLE [dbo].[TenantLogos] WITH CHECK ADD CONSTRAINT [FK__TenantLog__Tenan__0DB9F9A8]
FOREIGN KEY([TenantId])
REFERENCES [dbo].[Tenants] ([TenantId])
GO
ALTER TABLE [dbo].[TenantLogos] CHECK CONSTRAINT [FK__TenantLog__Tenan__0DB9F9A8]
GO

ALTER TABLE [dbo].[ticketAttachments] WITH CHECK ADD CONSTRAINT [FK__ticketAtt__Ticke__2FEF161B]
FOREIGN KEY([TicketId])
REFERENCES [dbo].[Tickets] ([TicketId])
GO
ALTER TABLE [dbo].[ticketAttachments] CHECK CONSTRAINT [FK__ticketAtt__Ticke__2FEF161B]
GO

ALTER TABLE [dbo].[ticketAttachments] WITH CHECK ADD CONSTRAINT [FK__ticketAtt__Ticke__30E33A54]
FOREIGN KEY([TicketMessageId])
REFERENCES [dbo].[ticketMessages] ([TicketMessageId])
GO
ALTER TABLE [dbo].[ticketAttachments] CHECK CONSTRAINT [FK__ticketAtt__Ticke__30E33A54]
GO

ALTER TABLE [dbo].[ticketMessages] WITH CHECK ADD CONSTRAINT [FK__ticketMes__Ticke__2C1E8537]
FOREIGN KEY([TicketId])
REFERENCES [dbo].[Tickets] ([TicketId])
GO
ALTER TABLE [dbo].[ticketMessages] CHECK CONSTRAINT [FK__ticketMes__Ticke__2C1E8537]
GO

ALTER TABLE [dbo].[ticketMessages] WITH CHECK ADD CONSTRAINT [FK__ticketMes__UserI__2D12A970]
FOREIGN KEY([UserId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[ticketMessages] CHECK CONSTRAINT [FK__ticketMes__UserI__2D12A970]
GO

ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK__Tickets__Created__284DF453]
FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Tickets] CHECK CONSTRAINT [FK__Tickets__Created__284DF453]
GO

ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK__Tickets__Assigne__2942188C]
FOREIGN KEY([AssignedTo])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Tickets] CHECK CONSTRAINT [FK__Tickets__Assigne__2942188C]
GO

ALTER TABLE [dbo].[TimeOffBalances] WITH CHECK ADD CONSTRAINT [FK_TimeOffBalances_Employee]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeOffBalances] CHECK CONSTRAINT [FK_TimeOffBalances_Employee]
GO

ALTER TABLE [dbo].[TimeOffRequests] WITH CHECK ADD CONSTRAINT [FK_TimeOffRequests_Employee]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeOffRequests] CHECK CONSTRAINT [FK_TimeOffRequests_Employee]
GO

ALTER TABLE [dbo].[TimeOffRequests] WITH CHECK ADD CONSTRAINT [FK_TimeOffRequests_ReviewedBy]
FOREIGN KEY([ReviewedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeOffRequests] CHECK CONSTRAINT [FK_TimeOffRequests_ReviewedBy]
GO


-- =============================================
-- BACKUP SUMMARY
-- =============================================
-- Total Tables: 21
-- Total Records: 348
-- 
-- Data per table:
--   Countries: 5 records
--   Employees: 47 records
--   Roles: 5 records
--   EmployeeRoles: 57 records
--   Tenants: 3 records
--   ExternalUsers: 6 records
--   HardwareInventory: 22 records
--   Licenses: 60 records
--   Modules: 12 records
--   RoleModules: 27 records
--   TenantLogos: 2 records
--   Tickets: 69 records
--   ticketMessages: 19 records
--   ticketAttachments: 4 records
--   TimeOffBalances: 4 records
--   TimeOffRequests: 6 records
-- =============================================

PRINT 'Complete backup restored successfully!'
PRINT 'Total records inserted: 348'
GO
