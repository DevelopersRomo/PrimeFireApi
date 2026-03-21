USE [devromo]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-03-20 22:14:21 ******/
/****** Database: devromo on A2NWPLSK14SQL-v05.shr.prod.iad2.secureserver.net ******/
/****** This script contains ALL table structures and ALL data ******/

-- =============================================
-- DROP ALL TABLES
-- =============================================

IF OBJECT_ID('dbo.TimeSheetSettings', 'U') IS NOT NULL
    DROP TABLE dbo.TimeSheetSettings;
GO

IF OBJECT_ID('dbo.TimeSheetPunches', 'U') IS NOT NULL
    DROP TABLE dbo.TimeSheetPunches;
GO

IF OBJECT_ID('dbo.TimeSheetLocationSnapshots', 'U') IS NOT NULL
    DROP TABLE dbo.TimeSheetLocationSnapshots;
GO

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

IF OBJECT_ID('dbo.Quotations', 'U') IS NOT NULL
    DROP TABLE dbo.Quotations;
GO

IF OBJECT_ID('dbo.QuotationItems', 'U') IS NOT NULL
    DROP TABLE dbo.QuotationItems;
GO

IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL
    DROP TABLE dbo.Products;
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

IF OBJECT_ID('dbo.Customers', 'U') IS NOT NULL
    DROP TABLE dbo.Customers;
GO

IF OBJECT_ID('dbo.CustomerNotes', 'U') IS NOT NULL
    DROP TABLE dbo.CustomerNotes;
GO

IF OBJECT_ID('dbo.CustomerAttachments', 'U') IS NOT NULL
    DROP TABLE dbo.CustomerAttachments;
GO

IF OBJECT_ID('dbo.CustomerAlternateContacts', 'U') IS NOT NULL
    DROP TABLE dbo.CustomerAlternateContacts;
GO

IF OBJECT_ID('dbo.Curriculums', 'U') IS NOT NULL
    DROP TABLE dbo.Curriculums;
GO

IF OBJECT_ID('dbo.Countries', 'U') IS NOT NULL
    DROP TABLE dbo.Countries;
GO

IF OBJECT_ID('dbo.Addresses', 'U') IS NOT NULL
    DROP TABLE dbo.Addresses;
GO


-- =============================================
-- CREATE ALL TABLES
-- =============================================

-- =============================================
-- Table: Addresses
-- =============================================

CREATE TABLE [dbo].[Addresses](
    [AddressId] [int] IDENTITY(1,1) NOT NULL,
    [Address1] [nvarchar](200) NOT NULL,
    [Address2] [nvarchar](200) NULL,
    [City] [nvarchar](100) NOT NULL,
    [State] [nvarchar](100) NOT NULL,
    [ZipCode] [nvarchar](20) NOT NULL,
    [CountryId] [int] NOT NULL,
    [GooglePlaceId] [nvarchar](255) NULL,
    [IsValidated] [bit] NOT NULL DEFAULT ((0)),
    [ValidatedAt] [datetime2] NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK_Addresses] PRIMARY KEY CLUSTERED
(
    [AddressId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

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
-- Table: CustomerAlternateContacts
-- =============================================

CREATE TABLE [dbo].[CustomerAlternateContacts](
    [CustomerAlternateContactId] [int] IDENTITY(1,1) NOT NULL,
    [CustomerId] [int] NOT NULL,
    [Name] [nvarchar](200) NOT NULL,
    [Email] [nvarchar](255) NULL,
    [Phone] [nvarchar](20) NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [UpdatedAt] [datetime2] NULL,
 CONSTRAINT [PK_CustomerAlternateContacts] PRIMARY KEY CLUSTERED
(
    [CustomerAlternateContactId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: CustomerAttachments
-- =============================================

CREATE TABLE [dbo].[CustomerAttachments](
    [CustomerAttachmentId] [int] IDENTITY(1,1) NOT NULL,
    [CustomerId] [int] NOT NULL,
    [FileName] [nvarchar](255) NOT NULL,
    [FileType] [nvarchar](100) NULL,
    [FilePath] [nvarchar](500) NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [CreatedBy] [int] NOT NULL,
 CONSTRAINT [PK_CustomerAttachments] PRIMARY KEY CLUSTERED
(
    [CustomerAttachmentId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: CustomerNotes
-- =============================================

CREATE TABLE [dbo].[CustomerNotes](
    [CustomerNoteId] [int] IDENTITY(1,1) NOT NULL,
    [CustomerId] [int] NOT NULL,
    [NoteText] [nvarchar](MAX) NOT NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [UpdatedAt] [datetime2] NULL,
    [CreatedBy] [int] NOT NULL,
 CONSTRAINT [PK_CustomerNotes] PRIMARY KEY CLUSTERED
(
    [CustomerNoteId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Customers
-- =============================================

CREATE TABLE [dbo].[Customers](
    [CustomerId] [int] IDENTITY(1,1) NOT NULL,
    [CustomerType] [nvarchar](20) NOT NULL,
    [CompanyName] [nvarchar](200) NULL,
    [FirstName] [nvarchar](100) NULL,
    [LastName] [nvarchar](100) NULL,
    [AdditionalName] [nvarchar](100) NULL,
    [Market] [nvarchar](50) NULL,
    [DtdPotential] [nvarchar](20) NULL,
    [PrimaryEmail] [nvarchar](255) NULL,
    [PrimaryPhone] [nvarchar](20) NULL,
    [PrimaryAddressId] [int] NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [UpdatedAt] [datetime2] NULL,
    [CreatedBy] [int] NOT NULL,
 CONSTRAINT [PK_Customers] PRIMARY KEY CLUSTERED
(
    [CustomerId] ASC
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
    [ManagerEmployeeId] [int] NULL,
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
    [Notes] [nvarchar](500) NULL,
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
-- Table: Products
-- =============================================

CREATE TABLE [dbo].[Products](
    [Id] [int] IDENTITY(1,1) NOT NULL,
    [Name] [nvarchar](200) NOT NULL,
    [Description] [nvarchar](2000) NULL,
    [Type] [varchar](20) NOT NULL,
    [SKU] [nvarchar](100) NULL,
    [UnitPrice] [numeric](18,2) NOT NULL DEFAULT ((0)),
    [Cost] [numeric](18,2) NOT NULL DEFAULT ((0)),
    [TaxRate] [numeric](5,2) NOT NULL DEFAULT ((0)),
    [Unit] [nvarchar](50) NOT NULL DEFAULT ('pieza'),
    [StockQuantity] [int] NOT NULL DEFAULT ((0)),
    [IsActive] [bit] NOT NULL DEFAULT ((1)),
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysdatetime()),
 CONSTRAINT [PK__Products__3214EC07AAF87C3C] PRIMARY KEY CLUSTERED
(
    [Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: QuotationItems
-- =============================================

CREATE TABLE [dbo].[QuotationItems](
    [Id] [int] IDENTITY(1,1) NOT NULL,
    [QuotationId] [int] NOT NULL,
    [ProductId] [int] NOT NULL,
    [Description] [nvarchar](1000) NULL,
    [Quantity] [decimal](18,2) NOT NULL DEFAULT ((1)),
    [UnitPrice] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Total] [decimal](18,2) NOT NULL DEFAULT ((0)),
 CONSTRAINT [PK__Quotatio__3214EC0771223114] PRIMARY KEY CLUSTERED
(
    [Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: Quotations
-- =============================================

CREATE TABLE [dbo].[Quotations](
    [Id] [int] IDENTITY(1,1) NOT NULL,
    [CustomerId] [int] NOT NULL,
    [QuoteDate] [datetime2] NOT NULL DEFAULT (sysdatetime()),
    [ExpirationDate] [datetime2] NULL,
    [Subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [Status] [varchar](20) NOT NULL DEFAULT ('Draft'),
    [Notes] [nvarchar](2000) NULL,
    [CreatedAt] [datetime2] NOT NULL DEFAULT (sysdatetime()),
 CONSTRAINT [PK__Quotatio__3214EC07AB66981D] PRIMARY KEY CLUSTERED
(
    [Id] ASC
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
    [TenantId] [int] NULL,
    [CreatedAt] [datetime] NOT NULL,
    [Email] [nvarchar](100) NULL,
    [PasswordHash] [nvarchar](255) NULL,
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
    [FavIcon] [nvarchar](500) NULL,
    [Email] [nvarchar](255) NULL,
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
-- Table: TimeSheetLocationSnapshots
-- =============================================

CREATE TABLE [dbo].[TimeSheetLocationSnapshots](
    [SnapshotId] [int] IDENTITY(1,1) NOT NULL,
    [EmployeeId] [int] NOT NULL,
    [CustomerId] [int] NULL,
    [IpAddress] [varchar](45) NULL,
    [Latitude] [varchar](20) NULL,
    [Longitude] [varchar](20) NULL,
    [GpsAccuracy] [varchar](20) NULL,
    [City] [varchar](100) NULL,
    [Region] [varchar](100) NULL,
    [Country] [varchar](100) NULL,
    [Timezone] [varchar](80) NULL,
    [LocationRaw] [varchar](MAX) NULL,
    [CapturedAt] [varchar](19) NOT NULL,
 CONSTRAINT [PK__TimeShee__664F572B28FA444D] PRIMARY KEY CLUSTERED
(
    [SnapshotId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TimeSheetPunches
-- =============================================

CREATE TABLE [dbo].[TimeSheetPunches](
    [PunchId] [int] IDENTITY(1,1) NOT NULL,
    [EmployeeId] [int] NOT NULL,
    [CustomerId] [int] NOT NULL,
    [ClockInAt] [varchar](19) NOT NULL,
    [ClockOutAt] [varchar](19) NULL,
    [Timezone] [varchar](80) NULL,
    [IpAddress] [varchar](45) NULL,
    [Latitude] [varchar](20) NULL,
    [Longitude] [varchar](20) NULL,
    [GpsAccuracy] [varchar](20) NULL,
    [City] [varchar](100) NULL,
    [Region] [varchar](100) NULL,
    [Country] [varchar](100) NULL,
    [LocationRaw] [varchar](MAX) NULL,
    [WorkedMinutes] [int] NOT NULL,
    [Status] [varchar](20) NOT NULL,
    [Note] [varchar](2000) NULL,
    [ApprovedBy] [int] NULL,
    [ApprovedAt] [varchar](19) NULL,
    [CreatedAt] [varchar](19) NOT NULL,
    [UpdatedAt] [varchar](19) NOT NULL,
 CONSTRAINT [PK__TimeShee__F6292C23063FBF56] PRIMARY KEY CLUSTERED
(
    [PunchId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: TimeSheetSettings
-- =============================================

CREATE TABLE [dbo].[TimeSheetSettings](
    [SettingId] [int] IDENTITY(1,1) NOT NULL,
    [OvertimeDailyHours] [varchar](10) NOT NULL,
    [OvertimeWeeklyHours] [varchar](10) NULL,
    [RoundToMinutes] [int] NULL,
    [IsActive] [bit] NOT NULL,
    [CreatedAt] [varchar](19) NOT NULL,
    [UpdatedAt] [varchar](19) NOT NULL,
    [MaxOvertimeDailyHours] [nvarchar](10) NULL,
 CONSTRAINT [PK__TimeShee__54372B1D995BD25A] PRIMARY KEY CLUSTERED
(
    [SettingId] ASC
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


-- Data for Addresses (7 records)
SET IDENTITY_INSERT [dbo].[Addresses] ON
GO

INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (1, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, '2026-02-01 02:00:09')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (2, N'Highway 8860 Km 1.2. Camino Matienzo Cintrón', NULL, N'Trujillo Alto,', N'Puerto Rico', N'00977', 1, NULL, 0, NULL, '2026-02-06 00:14:22')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (3, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, '2026-02-23 23:49:35')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (4, N'Highway 8860 Km 1.2', NULL, N'Trujillo Alto', N'PR', N'00977', 2, NULL, 0, NULL, '2026-02-23 23:52:39')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (5, N'10670 N Central Expy', NULL, N'Dallas', N'Texas', N'75231', 1, NULL, 0, NULL, '2026-02-23 23:57:15')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (6, N'N Henderson ave suite #308', NULL, N'Dallas', N'75206', N'75206', 1, NULL, 0, NULL, '2026-02-24 00:02:52')
INSERT [dbo].[Addresses] ([AddressId], [Address1], [Address2], [City], [State], [ZipCode], [CountryId], [GooglePlaceId], [IsValidated], [ValidatedAt], [CreatedAt]) VALUES (7, N'Office', NULL, N'Dallas', N'TX', N'75224', 1, NULL, 0, NULL, '2026-02-24 00:09:21')

SET IDENTITY_INSERT [dbo].[Addresses] OFF
GO


-- Curriculums: No data to insert


-- Data for Employees (50 records)
SET IDENTITY_INSERT [dbo].[Employees] ON
GO

INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (1, N'Juan', N'Carlos', N'Juan Carlos', N'Developer', N'IT', N'MX', N'jcarlos.villa.rivera@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'292367b5-7d70-4d13-81cb-ee6f7c650275', NULL, NULL, NULL, N'$2b$12$86/wa5zSinRGMtad4BiNrO77K9zNAUPRTpQl3KtGABf6/E3LqS5hq', NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (2, N'Jonathan', N'Romo', N'Jonathan Romo', N'External User', N'IT', N'MTY', N'info@devromo.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'08a89d51-b7c7-404a-9d2b-ee9f7440d63c', NULL, NULL, NULL, N'$2b$12$Zq0QadTdL/6ESgImpwBxT.zKkVns1Wrqrj8W9LkKrSxYRHoEswynC', N'jony.romo001', N'jony_romo@hotmail.com', 142)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (142, N'Eli', N'Romo', N'jony.romo001', N'External User', NULL, NULL, N'jony_romo@hotmail.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'7dffa13b-fe6f-4406-b429-93694b40284e', NULL, NULL, NULL, N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG', N'Jonathan Romo', N'info@devromo.com', 2)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (143, N'Adolfo', N'Martinez', N'Adolfo Martinez', N'Manager Alarm Designer', N'Engineering Alarms', N'Home Office TX', N'amartinez@primefire.us', NULL, N'+1 4075584334', N'+1 4075584334', N'Dallas, TX', N'Dallas', N'Texas (TX)', N'75202', 1, N'1e7152f1-aaf5-4789-9da4-e74d9b586843', N'amartinez@primefire.us', '2026-03-13 00:46:39', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (144, N'Jose Alberto', N'Rodriguez', N'Jose Alberto Rodriguez', N'President & CEO', N'President', N'Trujillo Alto, Puerto Rico', N'arodriguez@primefire.us', NULL, N'+1 7872212121', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b826abb3-30c8-4369-8d87-ce0d648e7fba', N'arodriguez@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (145, N'Baxter', N'Jayuya', N'Baxter Jayuya', N'Engineering Alarm', N'Engineering Alarm Designer', N'Guaynabo, Puerto Rico', N'bjayuya@primefire.us', NULL, NULL, N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'b9de2f69-4aba-42f3-87eb-da0e1dcf2cfa', N'bjayuya@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (146, N'Christopher', N'Carballo Rosado', N'Christopher Carballo Rosado', N'Fire Alarm Manager', N'Alarm Project Manager', N'Guaynabo, Puerto Rico', N'ccarballo@primefire.us', NULL, N'+1 7872017346', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'd63e397b-31e7-424e-a2c3-993562347b04', N'ccarballo@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (147, N'Cesar', N'Figueroa Cruzado', N'Cesar Figueroa Cruzado', N'Group Leader', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'cfigueroa@primefire.us', NULL, N'+1 9398919203 ', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', NULL, N'b5ff98b3-be60-4693-aa6e-2553b941faff', N'cfigueroa@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (148, N'Jose Daniel', N'Agosto Rivera', N'Jose Daniel Agosto Rivera', NULL, NULL, NULL, N'dagosto@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'a5c57db5-230b-41c2-a0e7-0747f4512d2d', N'dagosto@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (149, NULL, NULL, N'Dominicana', NULL, NULL, NULL, N'dominicana@primefire.do', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'405c6850-50aa-490a-91f0-b666e016f12e', N'dominicana@primefire.do', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (150, N'Edwin', N'De Jesus', N'Edwin De Jesus', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'edejesus@primefire.us', NULL, N'+1 7876433660', N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1efe087c-1bd7-4e77-9ec3-5577519a9871', N'edejesus@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (151, N'Emmanuel', N'Desueza', N'Enmanuel Desueza', N'Project Coordinator', N'Field Technician, Office Assistant ', N'Santo Domingo, República Dominicana', N'edesueza@primefire.do', NULL, N'+1 8095011901', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'b0241d3b-03a7-45bf-a2fa-f06a76b9317d', N'edesueza@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (152, N'Edwin', N'Guilloty', N'Edwin Guilloty', N'Project Manager', N'Operations', N'Guaynabo, Puerto Rico', N'eguilloty@primefire.us', NULL, N'+1 7876433660', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'76025b90-b5a8-4ba7-809b-0da6685492f8', N'eguilloty@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (153, N'Elizaud', N'Hernandez', N'Elizaud Hernandez', N'Administration Manager', N'Administration', N'Trujillo Alto, Puerto Rico', N'ehernandez@primefire.us', NULL, N'+1 3867483621', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'ad15e516-906b-4e3f-8e4c-373134505755', N'ehernandez@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (154, N'Emilio', N'Melendez', N'Emilio Melendez', N'Field Tech', N'Logistics / Operations', N'Prime Fire DO', N'emelendez@primefire.do', NULL, NULL, NULL, N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominiaca', N'10109', 3, N'4c12442f-758b-4921-8188-b0167d3e6281', N'emelendez@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (155, N'Elionetzy', N'Santiago Adames', N'Elionetzy Santiago Adames', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto', N'esadames@primefire.us', NULL, N'+1 7874729866', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b892a33-b52b-4f24-9af1-941c3eceb183', N'esadames@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (156, N'Gustavo', N'Heredia', N'Gustavo Heredia', N'Designer ', NULL, NULL, N'gheredia@primefire.do', NULL, N'+1 8492854334', NULL, N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'44d8c9a2-c02f-41c7-85e0-50c9f92ec327', N'gheredia@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (157, N'Geurys Jabbart', N'Medrano Montero', N'Geurys Medrano', N'Global Inventory Manager', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'gmedrano@primefire.do', NULL, N'+1 8295594355', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6dc58092-0b27-431c-a2b6-353e2fcf4c49', N'gmedrano@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (158, N'Gustavo', N'Vazquez', N'Gustavo Vazquez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvazquez@primefire.us', NULL, N'1 (787) 312-7679', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'07e0c48e-bc49-4f58-9e3b-c391b4fe12c2', N'gvazquez@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (159, N'Giovanni', N'Velez', N'Giovanni Velez', N'Fire Alarm Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvelez@primefire.us', NULL, N'+1 7873700568', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8b6db431-ee49-46c2-be9a-2e89a493130a', N'gvelez@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (160, NULL, NULL, N'Info', NULL, NULL, NULL, N'info@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'53172d9b-ad7e-49e4-81ce-25c1c7656a3e', N'info@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (161, N'Israel', N'Nieves', N'Israel Nieves', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto, Puerto Rico', N'inieves@primefire.us', NULL, N'+1 7872047807', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'396751cd-b9ac-40e9-8122-dffb9341f319', N'inieves@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (162, N'Jonathan', N'Romo', N'Jonathan Romo', N'Admin Systems', N'IT', N'Home Office, Mexico', N'it@primefire.us', NULL, N'+528125356287', N'+528125356287', N'Arturo B de la Garza #4613', N'Monterrey', NULL, NULL, 4, N'8c882f2c-19f8-4f17-a1e8-d5644456ea65', N'it@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (163, N'Juan', N'Aybar', N'Juan Lehtenin', N'Fire Alarm Division', N'PrimeFire DO', N'República Dominica', N'jaybar@primefire.do', NULL, NULL, N'+1 8095011901', N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominicana', N'10109', 3, N'2a9640a5-897f-49c0-94f7-15a6f4d642c9', N'jaybar@primefire.do', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (164, N'Joskayra', N'de Jesus Medina', N'Joskayra de Jesus Medina', N'Engineering Alarm Designer & Accountant', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'jdejesus@primefire.do', NULL, N'+1 809-499-5821', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'df97493e-56d4-45fb-8a18-25a60dead4b5', N'jdejesus@primefire.do', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (165, N'Javier', N'Lopez Rivera', N'Javier Lopez Rivera', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jlopez@primefire.us', NULL, N'+1 9393399185', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'e809702b-2fb2-45d3-b486-04f66b89d725', N'jlopez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (166, N'Jose', N'Martínez', N'Jose Martínez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jmartinez@primefire.us', NULL, N'+1 787-948-3352', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1eb06cab-eeae-425b-bd0e-562d6eb89735', N'jmartinez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (167, N'Jose', N'Morales', N'Jose Morales', N'Group Leader', N'Sprinklers Division', N'Trujillo Alto, Puerto Rico', N'jmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'd96be71d-b61f-40e5-b973-94843acf7c47', N'jmorales@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (168, N'Juan', N'Villa', N'Juan Villa', N'Systems', N'IT', N'Home Office, Mexico', N'jvilla@primefire.us', NULL, N'+522282553841', N'+522282553841', N'Retorno Pantochica #3', N'Xalapa', N'Veracruz', N'91098', 4, N'0523631c-d286-4be5-9aaf-e33ac83b587c', N'jvilla@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (169, N'Kevin', N'Lopez', N'Kevin Lopez', NULL, NULL, NULL, N'klopez@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'ac51c4f9-269a-44a8-99b9-aae4220a7e4e', N'klopez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (170, N'Kevin', N'Morales', N'Kevin Morales', N'Administrative Assistant', N'HR Analyst', N'Trujillo Alto, Puerto Rico', N'kmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b7ae779-a20d-47d9-9680-ccf54568ae41', N'kmorales@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (171, N'Kristian', N'Torres', N'Kristian Torres', N'Field Tech', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ktorres@primefire.us', NULL, N'+1 4077059670', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'b02a129b-cb1f-4d22-ab12-acbbeb5291e2', N'ktorres@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (172, N'Luis', N'Belliard', N'Luis Belliard', N'Fire Sprinklers Designer', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'lbelliard@primefire.do', NULL, N'+1 8292222869', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6e029e87-b520-4def-8aed-9484162bee13', N'lbelliard@primefire.do', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (173, N'Luis', N'Burset', N'Luis Burset', N'Fire Sprinklers Designer', N'Designer', N'Home Office TX', N'lburset@primefire.us', NULL, N'+1 7874855008', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR', N'00976', 2, N'88b8d661-148d-4476-881c-d42f4d3ef96e', N'lburset@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (174, N'Luis', N'De Jesus', N'Luis De Jesus', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ldejesus@primefire.us', NULL, N'+1 7873909755', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8d91aafe-6b6d-4994-84d4-5108e4e7b0ca', N'ldejesus@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (175, N'Luis D', N'Lugo', N'Luis D Lugo', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'llugo@primefire.us', NULL, N'+1 7879514104', N'+1 7876306000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'542a5a99-aa6a-4ce9-8435-e42f587444b6', N'llugo@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (176, N'Luis', N'Nieves', N'Luis Nieves', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'lnieves@primefire.us', NULL, N'+1 7873641643', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'8f082fd0-cad1-4579-8305-08b31f95befd', N'lnieves@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (177, N'Max', N'Oliveras', N'Max Oliveras', N'Project Manager', N'Field Engineering', N'Trujillo Alto', N'moliveras@primefire.us', NULL, N'+ 787 607 7402', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'41b65f97-f746-46c2-b03a-9f0dffaefb19', N'moliveras@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (178, N'Marcos', N'Quiles', N'Marcos Quiles', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'mquiles@primefire.us', NULL, N'+1 7875257965', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'0f46165b-1617-4d70-82f4-f4768b01f90c', N'mquiles@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (179, N'Nathan', N'Gonzalez', N'Nathan Gonzalez', N'Engineering Alarm Designers', N'Engineering Alarm', N'Trujillo Alto, Puerto Rico', N'ngonzalez@primefire.us', NULL, N'+1 7879819444', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'c9d2250f-2b79-403f-9c13-fe11212f4ebb', N'ngonzalez@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (180, NULL, NULL, N'Printer Guaynabo', NULL, NULL, NULL, N'Printer-Guaynabo@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'5719f4d2-8092-48f8-a53a-d6f0e28bf8ea', N'Printer-Guaynabo@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (181, N'Rayneé', N'Fúnez Heredia', N'Rayneé Fúnez Heredia', N'Account Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'rfunez@primefire.us', NULL, N'+1 9392350216', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'ab01cd10-bff4-4620-b55e-0d0f1ab1d151', N'rfunez@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (182, N'Rosa M', N'Rivera', N'Rosa M Rivera', N'Project Manager - Ai Strategic Efficiency', N'Administration', N'Guaynabo', N'rmrivera@primefire.us', NULL, N'(787)975-9127', N'787-630-6000', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'aa1aafd1-f175-4595-9dc1-d018b8069d66', N'rmrivera@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (183, N'Rolando', N'Rivera', N'Rolando Rivera', N'Alarm Designer', NULL, N'Guaynabo, Puerto Rico', N'rrivera@primefire.us', NULL, N'+1 7872377217', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'706337f9-ef71-47cb-982f-2ca206383da3', N'rrivera@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (184, N'Sigfredo', N'Carrero', N'Sigfredo Carrero', N'General Manager / Sprinkler Division', N'SubDirection', N'Trujillo Alto, Puerto Rico', N'scarrero@primefire.us', NULL, N'+1 7876475955', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b7d6932d-8c4c-411f-ab87-1547f9c07391', N'scarrero@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (185, NULL, NULL, N'service', NULL, NULL, NULL, N'service@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'f1228614-b6eb-4c3e-bbae-869139b6736e', N'service@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (186, N'Stephanie', N'Martinez', N'Stephanie Martinez', N'HR Analyst', N'Hiuman Resource', N'Trujillo Alto, Puerto Rico', N'smartinez@primefire.us', NULL, N'+1 8292485211', N'+1 8095011901', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'9cfcf921-1266-468c-a7de-0ee20fd472cb', N'smartinez@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (187, N'Santiago', N'Rodriguez', N'Santiago Rodriguez', N'Operation Manager', N'Field Engineering ', N'Santo Domingo, República Dominicana', N'srodriguez@primefire.do', NULL, N'+1 7876077402', N'+1 7877613180', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'635af9c2-ca37-4e5a-bfdd-989e0f7d14a9', N'srodriguez@primefire.do', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (188, N'Willian', N'Bencosme', N'Willian Bencosme', N'Engineering Alarm & Fire Sprinkler', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'wbencosme@primefire.do', NULL, N'+1 8297653844', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6987d8c8-0423-43bb-be3e-6601476147ab', N'wbencosme@primefire.do', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[Employees] ([EmployeeId], [FirstName], [LastName], [DisplayName], [Title], [Department], [Office], [Email], [Phone], [MobilePhone], [OfficePhone], [StreetAddress], [City], [State], [PostalCode], [CountryId], [AzureOid], [AzureUpn], [LastSyncedAt], [Anydesk], [PasswordHash], [Manager], [ManagerEmail], [ManagerEmployeeId]) VALUES (189, N'Wilnelia', N'Santos', N'Wilnelia Santos', N'HR Analyst', N'Hiuman Resource', N'Republica Dominicana', N'wsantos@primefire.us', NULL, N'+1 7877613180', N'+1 8608413625', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'be4788a5-f480-442d-ab40-209e317e54ac', N'wsantos@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[Employees] OFF
GO


-- Data for Customers (5 records)
SET IDENTITY_INSERT [dbo].[Customers] ON
GO

INSERT [dbo].[Customers] ([CustomerId], [CustomerType], [CompanyName], [FirstName], [LastName], [AdditionalName], [Market], [DtdPotential], [PrimaryEmail], [PrimaryPhone], [PrimaryAddressId], [CreatedAt], [UpdatedAt], [CreatedBy]) VALUES (3, N'commercial', N'Romo Life Safety', N'Andres', N'Romo', N'Adrian', N'engineering', N'medium', N'andy@romofiresystems.com', N'+1 972 742 0081', 3, '2026-02-23 23:49:35', '2026-02-24 00:09:58', 2)
INSERT [dbo].[Customers] ([CustomerId], [CustomerType], [CompanyName], [FirstName], [LastName], [AdditionalName], [Market], [DtdPotential], [PrimaryEmail], [PrimaryPhone], [PrimaryAddressId], [CreatedAt], [UpdatedAt], [CreatedBy]) VALUES (4, N'commercial', N'PrimeFire', N'Alberto', NULL, N'Rodriguez', N'engineering', N'high', N'arodriguez@primefire.us', N'+ 1 787 221 2121', 4, '2026-02-23 23:52:39', '2026-02-23 23:53:16', 2)
INSERT [dbo].[Customers] ([CustomerId], [CustomerType], [CompanyName], [FirstName], [LastName], [AdditionalName], [Market], [DtdPotential], [PrimaryEmail], [PrimaryPhone], [PrimaryAddressId], [CreatedAt], [UpdatedAt], [CreatedBy]) VALUES (5, N'commercial', N'Licensed Massage Pros', N'Virginia', N'Gonzalez', N'Gonzalez', N'commercial', N'medium', N'lnfo@licensedmassagepros.com', N'+1 682 377 6189', 5, '2026-02-23 23:57:15', '2026-02-23 23:57:25', 2)
INSERT [dbo].[Customers] ([CustomerId], [CustomerType], [CompanyName], [FirstName], [LastName], [AdditionalName], [Market], [DtdPotential], [PrimaryEmail], [PrimaryPhone], [PrimaryAddressId], [CreatedAt], [UpdatedAt], [CreatedBy]) VALUES (6, N'commercial', N'Havana NRG', N'Mariela', N'Suarez', NULL, N'individual', N'medium', N'havananrgbookings@gmail.com', N'+1 214 597 1970', 6, '2026-02-24 00:02:52', '2026-02-24 00:09:36', 2)
INSERT [dbo].[Customers] ([CustomerId], [CustomerType], [CompanyName], [FirstName], [LastName], [AdditionalName], [Market], [DtdPotential], [PrimaryEmail], [PrimaryPhone], [PrimaryAddressId], [CreatedAt], [UpdatedAt], [CreatedBy]) VALUES (7, N'commercial', N'Speedy Gonzalez Welding', N'Mireya', N'Gomez', NULL, N'individual', N'medium', N'speedygonzalezwelding@gmail.com', N'+1 (214) 284-1088', 7, '2026-02-24 00:09:22', NULL, 2)

SET IDENTITY_INSERT [dbo].[Customers] OFF
GO


-- CustomerAlternateContacts: No data to insert


-- CustomerAttachments: No data to insert


-- CustomerNotes: No data to insert


-- Departments: No data to insert


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


-- Data for EmployeeRoles (3 records)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (1, 1)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (1, 2)
INSERT [dbo].[EmployeeRoles] ([EmployeeId], [RoleId]) VALUES (2, 1)
GO


-- Data for Tenants (1 records)
SET IDENTITY_INSERT [dbo].[Tenants] ON
GO

INSERT [dbo].[Tenants] ([TenantId], [Name], [DbConnectionKey], [Description], [IsActive], [CreatedAt]) VALUES (1, N'DevRomo', N'MAIN', N'Developer''s Romo', 1, '2026-01-25 18:49:45')

SET IDENTITY_INSERT [dbo].[Tenants] OFF
GO


-- ExternalUsers: No data to insert


-- Data for HardwareInventory (2 records)
SET IDENTITY_INSERT [dbo].[HardwareInventory] ON
GO

INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (2, N'AA18250', N'Dell', N'Alienware 18 Area 51 AA18250', N'Laptop', N'Intel Core TM Ultra 9 275H', NULL, N'NVMe', 1860, NULL, N'Windows 11 Pro', '2025-11-12', '2026-11-12', '2025-11-12', 2, N'Dallas ', N'Active', N'Laptop Andy Principal ', '2026-02-19 23:51:48', NULL)
INSERT [dbo].[HardwareInventory] ([HardwareID], [SerialNumber], [Brand], [Model], [DeviceType], [Processor], [RAM_GB], [StorageType], [StorageSize_GB], [GPU], [OperatingSystem], [WarrantyStartDate], [WarrantyEndDate], [PurchaseDate], [EmployeeId], [Location], [Status], [Notes], [CreatedAt], [UpdatedAt]) VALUES (3, N'6L7KQ73', N'Dell', N'Alienware ', N'Laptop', N'Intel Core(TM) i9-10900 CPU', NULL, N'NVMe', 954, NULL, N'Windows 11 Home', '2023-01-01', '2024-01-01', '2023-01-01', 2, N'Grand Preire ', N'Active', N'Laptop de Backup', '2026-02-20 22:42:42', NULL)

SET IDENTITY_INSERT [dbo].[HardwareInventory] OFF
GO


-- Holidays: No data to insert


-- Jobs: No data to insert


-- Data for Licenses (32 records)
SET IDENTITY_INSERT [dbo].[Licenses] ON
GO

INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (1, N'Revit ', N'2025', '2025-03-10', '2026-03-10', N'Subscription', N'mmarquezia7@gmail.com', N'NA', 2, N'Licencia de Maria Angela ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (2, N'Revit ', N'2025', '2025-05-30', '2026-05-30', N'Subscription ', N'Barrioscastillosky@gmail.com', N'NA', 2, N'Licencia de Katherine Barrios')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (3, N'Revit ', N'2025', '2025-06-06', '2026-06-06', N'575-19015855', N'Rosiul.bulle@gmail.com', N'NA', 2, N'Licencia de Rosio Bulle')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (4, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'575-07753858', N'Oscar ', N'NA', 2, N'Licencia Oscar ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (5, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'574-60008874', N'Jose Gabriel Barrios', N'NA', 2, N'Licencia de Jose Gabriel Berrios')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (6, N'Revit ', N'2025', '2025-05-10', '2026-05-10', N'575-19015855', N'Ricardo Petit', N'NA', 2, N'Licencia de Ricardo Petit')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (7, N'Revit ', N'2026', '2025-09-24', '2026-09-24', N'jesusgazporua@gmail.com', N'Jesus Gonzalez', N'NA', 2, N'Licencia Jesus Gonzalez')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (8, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'575-19015855', N'Maria Jose', N'NA', 2, N'Licencia de María José: en octubre vence la de AutoCAD.')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (9, N'AutoCAD', N'2026', '2025-11-11', '2026-11-11', N'575-21731657-001R1', N'Henry Mujica', N'NA', 2, N'2 icencias AutoCAD Henry')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (10, N'AutoCAD', N'2026', '2025-11-11', '2026-11-11', N'575-21732053-001R1', N'Henry Mujica', N'NA', 2, N'Clientes Henry Mujica')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (11, N'Revit ', N'2025', '2025-12-05', '2026-12-05', N'574-60008874', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (12, N'Revit ', N'2025', '2025-12-05', '2026-12-05', N'574-73836720', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (13, N'Revit ', N'2025', '2025-09-01', '2026-09-01', N'Subscription', N'alirio.rojas@gmail.com', N'NA', 2, N'Cuenta de Alirio')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (14, N'McFee', N'Profesional', '2025-12-01', '2026-12-01', N'Subscription', N'Victor Valencia ', N'NA', 2, N'Se instalo Bluebeam y McFee
ahi que borrar la tarjeta de Credito de McFee')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (15, N'Revit ', N'2025', '2026-01-01', '2026-05-05', N'575-07754749', N'manueledu22@gmail.com/Manuel Jimenez', N'NA', 2, N'Se asigno la Licencia 575-07754749, pero no funciono. se cambio por subscripcion hay que recordar al proveedor cada 3 meses')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (16, N'Revit ', N'2025', '2026-03-10', '2027-03-10', N'vilchezwm@gmail.com', N'Wilhired Vilchez', N'NA', 2, N'Se habia instalado La Licencia con el Serial Number: 575-46607110, pero no funciono se instalo con proveedor y hay que renovar cada 3 meses ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (17, N'AutoCAD ', N'2026', '2025-12-01', '2026-12-01', N'jony_romo@hotmail.com', N'Andy Romo', N'NA', 2, N'Licencia por subscripcion ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (18, N'Windows ', N'11 Pro', '2025-12-01', '2030-12-31', N'9X4N6-W26CD-3MK3M-6VK4R-7H66T', N'Roby Romo RLS', N'NA', 2, N'Licencia W11 Pro Roberto Romo')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (19, N'McFee', N'Antivirus Plus', '2026-05-27', '2027-05-27', N'Subscription', N'info@devromo.com', N'NA', 2, N'Antivirys McFee
Activo en computadora personal,
Roby, Aryanna, Andy')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (20, N'ZerosSSL', N'Certificado SSL', '2026-01-01', '2027-01-01', N'Subscription', N'eliasvillegazcruz@gmail.com', N'NA', 2, N'Cuenta que hay que pagar anualmente con Elias')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (25, N'Godaddy', N'Webpage RLS', '2026-01-27', '2027-01-27', N'Subscripcion', N'andy@romolifesafety.com', N'NA', 2, N'Cobro Anual Webpage: Dominio Certificado SSL, Hoting, Codigo QR ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (29, N'Godaddy ', N'Webpage SWG', '2026-02-01', '2027-02-01', N'Subscription', N'speedygonzalezwelding@gmail.com', N'NA', 2, N'Webpage: Hosting, Certificado SSL, (dominio) lo tiene en m365')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (30, N'Godaddy', N'Webpage La Masajista', '2025-06-01', '2026-06-01', N'Subscription', N'licensedmassagepros@gmail.com', N'NA', 2, N'Webpage: Dominio, Certificado SSL, QR y Hosting')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (33, N'Antivirus ', N'Trend maximum 3D', '2023-09-09', '2026-09-26', N'XRMQ-0013-9700-4517-504', N'Alejandro SEDE ', N'NA', 2, N'Licencia Antivirus Alejandro clínica SEDE ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (34, N'Godaddy', N'Webpage Havana NRNG', '2025-08-01', '2026-08-01', N'Subscription', N'havananrgbookings@gmail.com', N'NA', 2, N'Webpage: Havana NRG, Dominio, Certificado SSL, Código QR, Hosting ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (35, N'Windows ', N'11 Pro', '2026-01-28', '2039-12-31', N'RNHDG-JMWXP-RQCH6-FTRKX-V22KG', N'Info@romolifesafety.com', N'NA', 2, N'Licencia de Aryanna de RLS')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (36, N'AutoCAD ', N'2026', '2026-02-19', '2027-02-19', N'575-51419614-001R1', N'Henry Mujica', N'Na', 2, N'Licencia a Henry Mujica AutoCAD 2026 1 año, se cambio por una licencia de subscripcion')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (37, N'Revit ', N'Revit Subscription', '2026-02-20', '2027-02-20', N'ybuitragov@gmail.com', N'Henri Mujica', N'NA', 2, N'Licencia de Cliente de Henry Mujica')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (38, N'Revit ', N'2026', '2026-02-26', '2027-02-26', N'Subscription ', N'trossell5@gmail.com', N'NA', 2, N'Licencia de Henry Mujica ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (39, N'AutoCAD ', N'2025', '2026-03-02', '2027-02-22', N'575-50292219:001Q1', N'Oscar CA Services ', N'NA', 2, N'Licencia a Oscar pago la de 3 años pero solo se activo por un año el key tambien se instalo Sketchup')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (40, N'Surfshark ', N'VPN', '2026-03-16', '2026-05-16', N'Subscription Trial ', N'Jony.romo001@gmail.com', N'NA', 2, N'Subscripcion de Prueba ')
INSERT [dbo].[Licenses] ([LicenseId], [Software], [Version], [CreatedAt], [ExpiryDate], [Key], [Account], [Password], [EmployeeId], [Notes]) VALUES (41, N'Revit ', N'2026', '2026-03-17', '2027-03-17', N'Sibscription', N'montanezcristian@gmail.com', N'NA', 2, N'Licencia de Cristian Montanez')

SET IDENTITY_INSERT [dbo].[Licenses] OFF
GO


-- Data for Modules (16 records)
SET IDENTITY_INSERT [dbo].[Modules] ON
GO

INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard and analytics', N'dashboard', N'/dashboard', 1, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (3, N'Jobs', N'jobs', N'Job postings management', N'work', N'/jobs', 2, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (5, N'Licenses', N'licenses', N'Software licenses management', N'vpn_key', N'/licenses', 5, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (6, N'Administration', N'administration', N'System administration', N'settings', N'/config', 6, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'config/permissions/roles', 6, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (8, N'Permissions', N'permissions', N'Module permissions management', N'lock', N'/config/permissions', 9, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (10, N'Modules', N'modules', N'modules', N'Modules', N'/config/permissions/modules', 7, 1, 6, '2025-10-18 22:40:51')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (11, N'Employees', N'employees', N'Employees Module', N'People', N'/employees', 3, 1, NULL, '2025-10-19 17:31:12')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (12, N'Tickets', N'tickets', N'', N'', N'/tickets', 10, 1, NULL, '2025-10-28 02:24:35')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (13, N'Hardware Inventory', N'hardwareInventory', N'Modulo para gestionar inventario de equipos', N'settings', N'/hardware-inventory', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'', N'/time-off/calendar', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (16, N'customers', N'customers', N'customers', N'', N'customers', 0, 1, NULL, '2026-01-29 05:13:51')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (17, N'products', N'products', N'Module to handle products for proposals', N'', N'/products', 15, 1, 16, '2026-02-14 19:00:24')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (18, N'Timesheet', N'timesheet', N'timesheet', N'', N'/timesheet', 0, 1, NULL, '2026-02-26 03:19:55')
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId], [CreatedAt]) VALUES (19, N'Quotations', N'quotations', N'Module to create quotations to a existing or new customers', N'', N'/quotations', 19, 1, 16, '2026-03-07 11:32:24')

SET IDENTITY_INSERT [dbo].[Modules] OFF
GO


-- Data for Products (6 records)
SET IDENTITY_INSERT [dbo].[Products] ON
GO

INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (11, N'Webpages & Marketing Digital', N'Package! For only $1200 to $1800, you''ll receive everything you need to establish a strong online presence for your business. Our package includes:
•
A professionally designed website with 4-6 sections
•
A custom domain name
•
An SSL certificate to keep your site secure.
•
Search engine optimization to improve your online visibility.
•
A secure form for collecting customer information.
•
Analytics to track your website''s performance.', N'Service', N'NA', '1200.00', '1800.00', '0.00', N'licencia', 100, 1, '2026-02-25 01:23:14')
INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (13, N'Single QR ', N'QR multiporpouse Marketing', N'Product', N'NA', '5.00', '49.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:26:38')
INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (14, N'2 QR''s', N'Multiporpouse QR''s Marketing', N'Product', N'NA', '7.00', '69.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:29:51')
INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (15, N'3 QR''s', N'Multiporpuse Marketing', N'Product', N'NA', '10.00', '99.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:30:48')
INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (16, N'Landing Page', N'A single page website, also known as a one-page website, is a type of web business card that consists of only one HTML page. Unlike a traditional website, which has multiple pages and navigation menus, a single page website displays all the essential information on a single scrolling page.
- It is more user-friendly and mobile-friendly, as it eliminates the need for clicking and loading new pages
- It is more focused and concise, as it forces you to prioritize the most vital information and messages
- It is more engaging and interactive, as it can use animations, transitions, and effects to create a seamless and immersive experience for the visitors', N'Service', N'NA', '450.00', '800.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:46:01')
INSERT [dbo].[Products] ([Id], [Name], [Description], [Type], [SKU], [UnitPrice], [Cost], [TaxRate], [Unit], [StockQuantity], [IsActive], [CreatedAt]) VALUES (17, N'Business cards + Digital QR', N'A web business card, also known as a digital business card, electronic business card, or virtual business card, is the modern take on the traditional paper business card.
Instead of being printed on physical cardstock, a web business card is a webpage containing your contact information and professional details. Like a website, it can be designed and customized to reflect your personal brand.
Here is a breakdown of how web business cards work:
•
Function: Like a paper card, it displays your name, job title, company affiliation, contact details (phone, email), and potentially a website link.
•
Benefits: They offer several advantages over physical cards. They are more eco-friendly, easier to share digitally (email, text message), can be more visually engaging, and can even include interactive features like links to your social media profiles or online portfolios.', N'Service', N'NA', '250.00', '250.00', '0.00', N'licencia', 100, 1, '2026-03-08 07:44:37')

SET IDENTITY_INSERT [dbo].[Products] OFF
GO


-- Quotations: No data to insert


-- QuotationItems: No data to insert


-- Data for RoleModules (31 records)
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 3, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 5, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 6, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 7, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 8, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 10, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 11, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 12, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 13, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 14, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 15, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 16, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 17, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 18, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 19, 1, 1, 1, 1, 1, 1, 1, '2026-03-07 11:59:33')
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


-- Data for TenantEmployees (4 records)
SET IDENTITY_INSERT [dbo].[TenantEmployees] ON
GO

INSERT [dbo].[TenantEmployees] ([Id], [TenantId], [CreatedAt], [Email], [PasswordHash]) VALUES (2, 1, '2026-01-25 19:15:18', N'jcarlos.villa.rivera@gmail.com', N'$2b$12$7ICyqJKa.71h6sYo5E1eQurNLUG.RC1.m9vgguIiENvSviWT6/Kr2')
INSERT [dbo].[TenantEmployees] ([Id], [TenantId], [CreatedAt], [Email], [PasswordHash]) VALUES (4, 1, '2026-02-12 01:48:20', N'info@devromo.com', N'$2b$12$1t46DZil2fGeybd6TQ22Z.gUiyW8dXI4tMaU8/bEGLkSQNrqpfDCe')
INSERT [dbo].[TenantEmployees] ([Id], [TenantId], [CreatedAt], [Email], [PasswordHash]) VALUES (5, 1, '2026-03-05 04:00:10', N'javiermendozar73@gmail.com', N'$2b$12$5BBcHMjwPW4SygLgge2Z6uY8eHthHOuigMPf7X8CQV3xGrCD1UQQ2')
INSERT [dbo].[TenantEmployees] ([Id], [TenantId], [CreatedAt], [Email], [PasswordHash]) VALUES (6, 1, '2026-03-12 23:51:03', N'jony.romo001@gmail.com', N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG')

SET IDENTITY_INSERT [dbo].[TenantEmployees] OFF
GO


-- Data for TenantLogos (2 records)
SET IDENTITY_INSERT [dbo].[TenantLogos] ON
GO

INSERT [dbo].[TenantLogos] ([LogoId], [TenantId], [Title], [Description], [Path], [PathBackground], [PrimaryColor], [SecondaryColor], [TertiaryColor], [CreatedAt], [UpdatedAt], [Url], [FavIcon], [Email]) VALUES (1, 1, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com', N'assets/fav/devromo.webp', NULL)
INSERT [dbo].[TenantLogos] ([LogoId], [TenantId], [Title], [Description], [Path], [PathBackground], [PrimaryColor], [SecondaryColor], [TertiaryColor], [CreatedAt], [UpdatedAt], [Url], [FavIcon], [Email]) VALUES (2, 1, N'Developer''s Romo Local', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', '2026-01-25 19:41:43', N'localhost:4201', N'assets/fav/devromo.webp', NULL)

SET IDENTITY_INSERT [dbo].[TenantLogos] OFF
GO


-- Tickets: No data to insert


-- ticketMessages: No data to insert


-- ticketAttachments: No data to insert


-- Data for TimeOffBalances (4 records)
SET IDENTITY_INSERT [dbo].[TimeOffBalances] ON
GO

INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (1, 2, N'personal', 2026, N'0', N'0', N'2.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (2, 2, N'vacation', 2026, N'0', N'0', N'5.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (3, 1, N'vacation', 2026, N'0', N'2.00', N'9.00', N'0')
INSERT [dbo].[TimeOffBalances] ([BalanceId], [EmployeeId], [AbsenceType], [Year], [EntitledDays], [UsedDays], [PendingDays], [CarryoverDays]) VALUES (4, 2, N'sick', 2026, N'0', N'0', N'1.00', N'0')

SET IDENTITY_INSERT [dbo].[TimeOffBalances] OFF
GO


-- Data for TimeOffRequests (3 records)
SET IDENTITY_INSERT [dbo].[TimeOffRequests] ON
GO

INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (18, 2, N'vacation', N'pending', N'full_day', N'2026-03-16', N'2026-03-16', NULL, NULL, NULL, N'1.00', N'holliday day', NULL, NULL, NULL, N'2026-03-13 00:17:12', N'2026-03-13 00:17:12')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (19, 2, N'personal', N'pending', N'full_day', N'2026-03-17', N'2026-03-17', NULL, NULL, NULL, N'1.00', N'i need to go to the doctor', NULL, NULL, NULL, N'2026-03-13 00:17:56', N'2026-03-13 00:17:56')
INSERT [dbo].[TimeOffRequests] ([RequestId], [EmployeeId], [AbsenceType], [Status], [TimeUnit], [StartDate], [EndDate], [StartTime], [EndTime], [TotalHours], [TotalDays], [Reason], [ReviewedBy], [ReviewedAt], [ReviewNotes], [CreatedAt], [UpdatedAt]) VALUES (20, 2, N'sick', N'pending', N'hours', N'2026-03-18', N'2026-03-18', N'15:00:00', N'23:00:00', N'8.00', N'1.00', N'I''m going to do internally', NULL, NULL, NULL, N'2026-03-13 00:18:49', N'2026-03-13 00:18:49')

SET IDENTITY_INSERT [dbo].[TimeOffRequests] OFF
GO


-- Data for TimeSheetLocationSnapshots (10 records)
SET IDENTITY_INSERT [dbo].[TimeSheetLocationSnapshots] ON
GO

INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (1, 1, 4, N'189.159.68.227:37844', N'25.677453', N'-100.2997179', N'11.47599983215332', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 04:31:41')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (2, 1, 4, N'189.159.68.227:57206', N'25.6774467', N'-100.299719', N'11.557000160217285', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 04:59:24')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (3, 2, 4, N'201.172.174.87:62231', N'25.76914415426781', N'-100.45508858796572', N'9.315270587075704', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 11:58:16')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (4, 2, 4, N'201.162.217.161:21712', N'25.719697193041487', N'-100.53277470156657', N'11.475186144311264', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 21:51:05')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (5, 2, 4, N'201.162.227.161:53100', N'25.71964568523301', N'-100.53277502193406', N'14.265556591242005', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-27 13:01:45')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (6, 2, 4, N'201.172.174.87:60879', N'25.76917236443903', N'-100.45506374825243', N'8.891461397408264', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 00:09:43')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (7, 2, 4, N'201.162.168.172:4275', N'25.724477216666667', N'-100.53745165000001', N'5', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 13:10:57')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (8, 2, 4, N'201.162.168.172:12222', N'25.720080033597593', N'-100.52831530355449', N'9.500300647485515', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 17:05:45')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (9, 2, 4, N'200.68.165.218:24807', N'25.719692578624368', N'-100.53276596899278', N'10.629695559329345', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-04 19:31:45')
INSERT [dbo].[TimeSheetLocationSnapshots] ([SnapshotId], [EmployeeId], [CustomerId], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [Timezone], [LocationRaw], [CapturedAt]) VALUES (10, 2, 4, N'201.172.174.87:51592', N'25.769172215123735', N'-100.45506324598706', N'11.542115847790958', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-05 01:09:33')

SET IDENTITY_INSERT [dbo].[TimeSheetLocationSnapshots] OFF
GO


-- Data for TimeSheetPunches (5 records)
SET IDENTITY_INSERT [dbo].[TimeSheetPunches] ON
GO

INSERT [dbo].[TimeSheetPunches] ([PunchId], [EmployeeId], [CustomerId], [ClockInAt], [ClockOutAt], [Timezone], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [LocationRaw], [WorkedMinutes], [Status], [Note], [ApprovedBy], [ApprovedAt], [CreatedAt], [UpdatedAt]) VALUES (1, 1, 4, N'2026-02-26 02:31:42', N'2026-02-26 11:59:25', N'America/Monterrey', NULL, N'25.6774467', N'-100.299719', N'11.557000160217285', NULL, NULL, NULL, NULL, 706, N'approved', N'Test', 1, N'2026-02-26 05:46:14', N'2026-02-26 04:31:42', N'2026-02-26 05:46:14')
INSERT [dbo].[TimeSheetPunches] ([PunchId], [EmployeeId], [CustomerId], [ClockInAt], [ClockOutAt], [Timezone], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [LocationRaw], [WorkedMinutes], [Status], [Note], [ApprovedBy], [ApprovedAt], [CreatedAt], [UpdatedAt]) VALUES (2, 2, 4, N'2026-02-26 11:58:17', N'2026-02-26 21:51:06', N'America/Monterrey', NULL, N'25.719697193041487', N'-100.53277470156657', N'11.475186144311264', NULL, NULL, NULL, NULL, 592, N'closed', N'Current working remote ', NULL, NULL, N'2026-02-26 11:58:17', N'2026-02-26 21:51:06')
INSERT [dbo].[TimeSheetPunches] ([PunchId], [EmployeeId], [CustomerId], [ClockInAt], [ClockOutAt], [Timezone], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [LocationRaw], [WorkedMinutes], [Status], [Note], [ApprovedBy], [ApprovedAt], [CreatedAt], [UpdatedAt]) VALUES (3, 2, 4, N'2026-02-27 13:01:46', N'2026-03-03 00:09:44', N'America/Monterrey', NULL, N'25.76917236443903', N'-100.45506374825243', N'8.891461397408264', NULL, NULL, NULL, NULL, 4987, N'closed', N'Working with prime fire in the app', NULL, NULL, N'2026-02-27 13:01:46', N'2026-03-03 00:09:44')
INSERT [dbo].[TimeSheetPunches] ([PunchId], [EmployeeId], [CustomerId], [ClockInAt], [ClockOutAt], [Timezone], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [LocationRaw], [WorkedMinutes], [Status], [Note], [ApprovedBy], [ApprovedAt], [CreatedAt], [UpdatedAt]) VALUES (4, 2, 4, N'2026-03-03 13:10:57', N'2026-03-03 17:05:49', N'America/Monterrey', NULL, N'25.720080033597593', N'-100.52831530355449', N'9.500300647485515', NULL, NULL, NULL, NULL, 234, N'closed', NULL, NULL, NULL, N'2026-03-03 13:10:57', N'2026-03-03 17:05:49')
INSERT [dbo].[TimeSheetPunches] ([PunchId], [EmployeeId], [CustomerId], [ClockInAt], [ClockOutAt], [Timezone], [IpAddress], [Latitude], [Longitude], [GpsAccuracy], [City], [Region], [Country], [LocationRaw], [WorkedMinutes], [Status], [Note], [ApprovedBy], [ApprovedAt], [CreatedAt], [UpdatedAt]) VALUES (5, 2, 4, N'2026-03-04 19:31:46', N'2026-03-05 01:09:34', N'America/Monterrey', NULL, N'25.769172215123735', N'-100.45506324598706', N'11.542115847790958', NULL, NULL, NULL, NULL, 337, N'closed', NULL, NULL, NULL, N'2026-03-04 19:31:46', N'2026-03-05 01:09:34')

SET IDENTITY_INSERT [dbo].[TimeSheetPunches] OFF
GO


-- Data for TimeSheetSettings (1 records)
SET IDENTITY_INSERT [dbo].[TimeSheetSettings] ON
GO

INSERT [dbo].[TimeSheetSettings] ([SettingId], [OvertimeDailyHours], [OvertimeWeeklyHours], [RoundToMinutes], [IsActive], [CreatedAt], [UpdatedAt], [MaxOvertimeDailyHours]) VALUES (1, N'8.00', N'40.00', NULL, 1, N'2026-02-26 03:20:13', N'2026-02-26 03:20:13', N'8.00')

SET IDENTITY_INSERT [dbo].[TimeSheetSettings] OFF
GO


-- =============================================
-- FOREIGN KEYS
-- =============================================

ALTER TABLE [dbo].[Addresses] WITH CHECK ADD CONSTRAINT [FK_Addresses_Countries]
FOREIGN KEY([CountryId])
REFERENCES [dbo].[Countries] ([CountryId])
GO
ALTER TABLE [dbo].[Addresses] CHECK CONSTRAINT [FK_Addresses_Countries]
GO

ALTER TABLE [dbo].[CustomerAlternateContacts] WITH CHECK ADD CONSTRAINT [FK_CustomerAlternateContacts_CustomerId_Customers]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[CustomerAlternateContacts] CHECK CONSTRAINT [FK_CustomerAlternateContacts_CustomerId_Customers]
GO

ALTER TABLE [dbo].[CustomerAttachments] WITH CHECK ADD CONSTRAINT [FK_CustomerAttachments_CustomerId_Customers]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[CustomerAttachments] CHECK CONSTRAINT [FK_CustomerAttachments_CustomerId_Customers]
GO

ALTER TABLE [dbo].[CustomerAttachments] WITH CHECK ADD CONSTRAINT [FK_CustomerAttachments_CreatedBy_Employees]
FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[CustomerAttachments] CHECK CONSTRAINT [FK_CustomerAttachments_CreatedBy_Employees]
GO

ALTER TABLE [dbo].[CustomerNotes] WITH CHECK ADD CONSTRAINT [FK_CustomerNotes_CustomerId_Customers]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[CustomerNotes] CHECK CONSTRAINT [FK_CustomerNotes_CustomerId_Customers]
GO

ALTER TABLE [dbo].[CustomerNotes] WITH CHECK ADD CONSTRAINT [FK_CustomerNotes_CreatedBy_Employees]
FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[CustomerNotes] CHECK CONSTRAINT [FK_CustomerNotes_CreatedBy_Employees]
GO

ALTER TABLE [dbo].[Customers] WITH CHECK ADD CONSTRAINT [FK_Customers_PrimaryAddressId_Addresses]
FOREIGN KEY([PrimaryAddressId])
REFERENCES [dbo].[Addresses] ([AddressId])
GO
ALTER TABLE [dbo].[Customers] CHECK CONSTRAINT [FK_Customers_PrimaryAddressId_Addresses]
GO

ALTER TABLE [dbo].[Customers] WITH CHECK ADD CONSTRAINT [FK_Customers_CreatedBy_Employees]
FOREIGN KEY([CreatedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Customers] CHECK CONSTRAINT [FK_Customers_CreatedBy_Employees]
GO

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

ALTER TABLE [dbo].[Employees] WITH CHECK ADD CONSTRAINT [FK_Employees_ManagerEmployee]
FOREIGN KEY([ManagerEmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Employees] CHECK CONSTRAINT [FK_Employees_ManagerEmployee]
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

ALTER TABLE [dbo].[QuotationItems] WITH CHECK ADD CONSTRAINT [FK_QuotationItems_Product]
FOREIGN KEY([ProductId])
REFERENCES [dbo].[Products] ([Id])
GO
ALTER TABLE [dbo].[QuotationItems] CHECK CONSTRAINT [FK_QuotationItems_Product]
GO

ALTER TABLE [dbo].[QuotationItems] WITH CHECK ADD CONSTRAINT [FK_QuotationItems_Quotation]
FOREIGN KEY([QuotationId])
REFERENCES [dbo].[Quotations] ([Id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[QuotationItems] CHECK CONSTRAINT [FK_QuotationItems_Quotation]
GO

ALTER TABLE [dbo].[Quotations] WITH CHECK ADD CONSTRAINT [FK_Quotations_Customers]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
GO
ALTER TABLE [dbo].[Quotations] CHECK CONSTRAINT [FK_Quotations_Customers]
GO

ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK__RoleModul__Modul__21A0F6C4]
FOREIGN KEY([ModuleId])
REFERENCES [dbo].[Modules] ([ModuleId])
GO
ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK__RoleModul__Modul__21A0F6C4]
GO

ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK__RoleModul__RoleI__20ACD28B]
FOREIGN KEY([RoleId])
REFERENCES [dbo].[Roles] ([RoleId])
GO
ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK__RoleModul__RoleI__20ACD28B]
GO

ALTER TABLE [dbo].[ticketAttachments] WITH CHECK ADD CONSTRAINT [FK__ticketAtt__Ticke__30E33A54]
FOREIGN KEY([TicketMessageId])
REFERENCES [dbo].[ticketMessages] ([TicketMessageId])
GO
ALTER TABLE [dbo].[ticketAttachments] CHECK CONSTRAINT [FK__ticketAtt__Ticke__30E33A54]
GO

ALTER TABLE [dbo].[ticketAttachments] WITH CHECK ADD CONSTRAINT [FK__ticketAtt__Ticke__2FEF161B]
FOREIGN KEY([TicketId])
REFERENCES [dbo].[Tickets] ([TicketId])
GO
ALTER TABLE [dbo].[ticketAttachments] CHECK CONSTRAINT [FK__ticketAtt__Ticke__2FEF161B]
GO

ALTER TABLE [dbo].[ticketMessages] WITH CHECK ADD CONSTRAINT [FK__ticketMes__UserI__2D12A970]
FOREIGN KEY([UserId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[ticketMessages] CHECK CONSTRAINT [FK__ticketMes__UserI__2D12A970]
GO

ALTER TABLE [dbo].[ticketMessages] WITH CHECK ADD CONSTRAINT [FK__ticketMes__Ticke__2C1E8537]
FOREIGN KEY([TicketId])
REFERENCES [dbo].[Tickets] ([TicketId])
GO
ALTER TABLE [dbo].[ticketMessages] CHECK CONSTRAINT [FK__ticketMes__Ticke__2C1E8537]
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

ALTER TABLE [dbo].[TimeSheetLocationSnapshots] WITH CHECK ADD CONSTRAINT [FK__TimeSheet__Custo__32AB8735]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
GO
ALTER TABLE [dbo].[TimeSheetLocationSnapshots] CHECK CONSTRAINT [FK__TimeSheet__Custo__32AB8735]
GO

ALTER TABLE [dbo].[TimeSheetLocationSnapshots] WITH CHECK ADD CONSTRAINT [FK__TimeSheet__Emplo__31B762FC]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeSheetLocationSnapshots] CHECK CONSTRAINT [FK__TimeSheet__Emplo__31B762FC]
GO

ALTER TABLE [dbo].[TimeSheetPunches] WITH CHECK ADD CONSTRAINT [FK__TimeSheet__Custo__2DE6D218]
FOREIGN KEY([CustomerId])
REFERENCES [dbo].[Customers] ([CustomerId])
GO
ALTER TABLE [dbo].[TimeSheetPunches] CHECK CONSTRAINT [FK__TimeSheet__Custo__2DE6D218]
GO

ALTER TABLE [dbo].[TimeSheetPunches] WITH CHECK ADD CONSTRAINT [FK__TimeSheet__Emplo__2CF2ADDF]
FOREIGN KEY([EmployeeId])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeSheetPunches] CHECK CONSTRAINT [FK__TimeSheet__Emplo__2CF2ADDF]
GO

ALTER TABLE [dbo].[TimeSheetPunches] WITH CHECK ADD CONSTRAINT [FK__TimeSheet__Appro__2EDAF651]
FOREIGN KEY([ApprovedBy])
REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[TimeSheetPunches] CHECK CONSTRAINT [FK__TimeSheet__Appro__2EDAF651]
GO


-- =============================================
-- BACKUP SUMMARY
-- =============================================
-- Total Tables: 32
-- Total Records: 192
-- 
-- Data per table:
--   Countries: 5 records
--   Addresses: 7 records
--   Employees: 50 records
--   Customers: 5 records
--   Roles: 5 records
--   EmployeeRoles: 3 records
--   Tenants: 1 records
--   HardwareInventory: 2 records
--   Licenses: 32 records
--   Modules: 16 records
--   Products: 6 records
--   RoleModules: 31 records
--   TenantEmployees: 4 records
--   TenantLogos: 2 records
--   TimeOffBalances: 4 records
--   TimeOffRequests: 3 records
--   TimeSheetLocationSnapshots: 10 records
--   TimeSheetPunches: 5 records
--   TimeSheetSettings: 1 records
-- =============================================

PRINT 'Complete backup restored successfully!'
PRINT 'Total records inserted: 192'
GO
