USE [PrimeFireCorp]
GO

/****** PARTIAL DATABASE BACKUP ******/
/****** Generated: 2026-01-13 17:56:17 ******/
/****** This script contains ALL table structures and data for: Countries, Roles, Modules, RoleModules ******/

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
-- INSERT DATA FOR SPECIFIC TABLES
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
-- Tables with data: Countries, Roles, Modules, RoleModules
--   Countries: 5 records
--   Roles: 5 records
--   Modules: 12 records
--   RoleModules: 27 records
-- Total Records: 49
-- =============================================

PRINT 'Partial backup restored successfully!'
PRINT 'Total records inserted: 49'
GO
