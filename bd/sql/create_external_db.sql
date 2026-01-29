-- Script to initialize a new External Tenant Database
-- This contains ALL necessary tables for the PrimeFire application
-- Updated to include Auth, Tickets, Modules, TimeOff, and HardwareInventory

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- 1. Core Tables (Countries, Roles, Departments)
-- =============================================
CREATE TABLE [dbo].[Countries](
	[CountryId] [smallint] IDENTITY(1,1) NOT NULL,
	[Name] [nvarchar](20) NULL,
 CONSTRAINT [PK_Country] PRIMARY KEY CLUSTERED ([CountryId] ASC)
)
GO

CREATE TABLE [dbo].[Roles](
	[RoleId] [int] IDENTITY(1,1) NOT NULL,
	[RoleName] [nvarchar](50) NOT NULL,
	[Description] [nvarchar](200) NULL,
 CONSTRAINT [PK_Roles] PRIMARY KEY CLUSTERED ([RoleId] ASC)
)
GO

CREATE TABLE [dbo].[Departments] (
    [DepartmentId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Departments PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL CONSTRAINT UQ_Departments_Name UNIQUE,
    [Code] NVARCHAR(20) NULL
)
GO

-- =============================================
-- 2. Employees & Auth
-- =============================================
CREATE TABLE [dbo].[Employees](
	[EmployeeId] [int] IDENTITY(1,1) NOT NULL,
	[FirstName] [nvarchar](50) NULL,
	[LastName] [nvarchar](50) NULL,
	[DisplayName] [nvarchar](100) NULL,
	[Title] [varchar](50) NULL,
	[Department] [nvarchar](50) NULL,
	[Office] [nvarchar](50) NULL,
	[Email] [nvarchar](50) NULL,
	[Phone] [nvarchar](20) NULL,
	[MobilePhone] [nvarchar](20) NULL,
	[OfficePhone] [nvarchar](20) NULL,
	[Anydesk] [nvarchar](50) NULL,
	[StreetAddress] [nvarchar](100) NULL,
	[City] [nvarchar](50) NULL,
	[State] [nvarchar](50) NULL,
	[PostalCode] [nvarchar](20) NULL,
	[CountryId] [smallint] NULL,
	[AzureOid] [nvarchar](100) NULL,
	[AzureUpn] [nvarchar](100) NULL,
    [PasswordHash] [nvarchar](255) NULL, -- Added for external authentication
	[LastSyncedAt] [datetime] NULL,
 CONSTRAINT [PK_Employees] PRIMARY KEY CLUSTERED ([EmployeeId] ASC),
 CONSTRAINT [UQ_Employees_AzureOid] UNIQUE ([AzureOid])
)
GO

CREATE TABLE [dbo].[EmployeeRoles](
	[EmployeeId] [int] NOT NULL,
	[RoleId] [int] NOT NULL,
 CONSTRAINT [PK_EmployeeRoles] PRIMARY KEY CLUSTERED ([EmployeeId] ASC, [RoleId] ASC)
)
GO

-- =============================================
-- 3. Tenant Management
-- =============================================
CREATE TABLE [dbo].[Tenants] (
    [TenantId] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL,
    [DbConnectionKey] NVARCHAR(50) NOT NULL,
    [Description] NVARCHAR(255),
    [IsActive] BIT DEFAULT 1,
    [CreatedAt] DATETIME2 DEFAULT GETDATE()
)
GO

CREATE TABLE [dbo].[TenantEmployees] (
    [Id] INT IDENTITY(1,1) PRIMARY KEY,
    [Email] NVARCHAR(100) NULL,
    [PasswordHash] NVARCHAR(255) NULL,
    [TenantId] INT NULL,
    [CreatedAt] DATETIME2 DEFAULT GETDATE()
)
GO

-- =============================================
-- 4. Business Logic Tables (Jobs, Curriculums, Licenses)
-- =============================================
CREATE TABLE [dbo].[Jobs](
	[JobId] [int] IDENTITY(1,1) NOT NULL,
	[Title] [nvarchar](100) NOT NULL,
	[Description] [nvarchar](1000) NULL,
	[Requirements] [nvarchar](1000) NULL,
	[Location] [nvarchar](100) NULL,
	[SalaryMin] [decimal](10, 2) NULL,
	[SalaryMax] [decimal](10, 2) NULL,
	[Status] [varchar](20) NOT NULL DEFAULT 'active',
	[PostedAt] [datetime] NOT NULL DEFAULT GETDATE(),
	[EmployeeId] [int] NULL,
	[CountryId] [smallint] NULL,
 CONSTRAINT [PK_Jobs] PRIMARY KEY CLUSTERED ([JobId] ASC)
)
GO

CREATE TABLE [dbo].[Curriculums](
	[CurriculumId] [int] IDENTITY(1,1) NOT NULL,
	[JobId] [int] NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
	[Email] [nvarchar](100) NOT NULL,
	[Phone] [nvarchar](20) NULL,
	[CurriculumPath] [nvarchar](255) NULL,
	[CoverLetter] [nvarchar](1000) NULL,
	[Status] [varchar](20) NOT NULL DEFAULT 'pending',
	[SubmittedAt] [datetime] NOT NULL DEFAULT GETDATE(),
	[EmployeeId] [int] NULL,
 CONSTRAINT [PK_Curriculums] PRIMARY KEY CLUSTERED ([CurriculumId] ASC)
)
GO

CREATE TABLE [dbo].[Licenses](
	[LicenseId] [smallint] IDENTITY(1,1) NOT NULL,
	[Software] [varchar](50) NULL,
	[Version] [varchar](20) NULL,
	[CreatedAt] [date] NULL,
	[ExpiryDate] [date] NULL,
	[Key] [varchar](50) NULL,
	[Account] [varchar](50) NULL,
	[Password] [varchar](50) NULL,
	[Notes] [nvarchar](255) NULL,
	[EmployeeId] [int] NULL,
 CONSTRAINT [PK_Licenses] PRIMARY KEY CLUSTERED ([LicenseId] ASC)
)
GO

-- =============================================
-- 5. Hardware Inventory
-- =============================================
CREATE TABLE [dbo].[HardwareInventory](
    [HardwareID] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [SerialNumber] [nvarchar](50) NOT NULL UNIQUE,
    [Brand] [nvarchar](50) NOT NULL,
    [Model] [nvarchar](100) NULL,
    [DeviceType] [nvarchar](20) NULL CHECK ([DeviceType] IN ('Laptop', 'Desktop', 'Workstation', 'Server')),
    [Processor] [nvarchar](100) NULL,
    [RAM_GB] [int] NULL,
    [StorageType] [nvarchar](20) NULL CHECK ([StorageType] IN ('HDD', 'SSD', 'NVMe', 'Hybrid')),
    [StorageSize_GB] [int] NULL,
    [GPU] [nvarchar](100) NULL,
    [OperatingSystem] [nvarchar](100) NULL,
    [WarrantyStartDate] [date] NULL,
    [WarrantyEndDate] [date] NULL,
    [PurchaseDate] [date] NULL,
    [EmployeeId] [int] NULL,
    [Location] [nvarchar](100) NULL,
    [Status] [nvarchar](20) DEFAULT 'Active' CHECK ([Status] IN ('Active', 'In Repair', 'Retired', 'Spare')),
    [Notes] [nvarchar](255) NULL,
    [CreatedAt] [datetime] DEFAULT GETDATE(),
    [UpdatedAt] [datetime] NULL
)
GO

-- =============================================
-- 6. Tickets System
-- =============================================
CREATE TABLE [dbo].[Tickets](
	[TicketId] [int] IDENTITY(1,1) NOT NULL,
	[Title] [nvarchar](200) NOT NULL,
	[Description] [nvarchar](2000) NULL,
	[Status] [nvarchar](20) NOT NULL DEFAULT ('todo') CHECK ([Status] IN ('todo', 'active', 'inactive', 'closed', 'done', 'in_progress', 'on_hold')),
	[Priority] [nvarchar](20) NOT NULL DEFAULT ('normal') CHECK ([Priority] IN ('low', 'normal', 'medium', 'high', 'urgent')),
	[SLA] [nvarchar](10) NULL CHECK ([SLA] IS NULL OR [SLA] IN ('12h', '24h', '48h', '1w', '2w', '4w')),
	[CreatedBy] [int] NOT NULL,
	[AssignedTo] [int] NULL,
	[CreatedAt] [datetime2](7) NOT NULL DEFAULT (SYSUTCDATETIME()),
	[UpdatedAt] [datetime2](7) NOT NULL DEFAULT (SYSUTCDATETIME()),
 CONSTRAINT [PK_Tickets] PRIMARY KEY CLUSTERED ([TicketId] ASC)
)
GO

CREATE TABLE [dbo].[ticketMessages](
    [TicketMessageId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [TicketId] INT NOT NULL,
    [UserId] INT NOT NULL,
    [MessageTxt] NVARCHAR(MAX) NULL,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    [UpdatedAt] DATETIME2 NULL,
    [EditedAt] DATETIME2 NULL
)
GO

CREATE TABLE [dbo].[ticketAttachments](
    [TicketAttachmentId] INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [TicketId] INT NOT NULL,
    [TicketMessageId] INT NULL,
    [FileName] NVARCHAR(255) NOT NULL,
    [FileType] NVARCHAR(100) NULL,
    [FilePath] NVARCHAR(500) NULL,
    [CreatedAt] DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
)
GO

-- =============================================
-- 7. Modules & Permissions
-- =============================================
CREATE TABLE [dbo].[Modules](
    [ModuleId] [int] IDENTITY(1,1) NOT NULL PRIMARY KEY,
    [ModuleName] [nvarchar](50) NOT NULL,
    [ModuleKey] [varchar](50) NOT NULL UNIQUE,
    [Description] [nvarchar](200) NULL,
    [Icon] [varchar](50) NULL,
    [RouteUrl] [varchar](100) NULL,
    [DisplayOrder] [int] NULL DEFAULT 0,
    [IsActive] [bit] NOT NULL DEFAULT 1,
    [ParentModuleId] [int] NULL,
    [CreatedAt] [datetime] NOT NULL DEFAULT GETDATE()
)
GO

CREATE TABLE [dbo].[RoleModules](
    [RoleId] [int] NOT NULL,
    [ModuleId] [int] NOT NULL,
    [CanView] [bit] NOT NULL DEFAULT 1,
    [CanCreate] [bit] NOT NULL DEFAULT 0,
    [CanEdit] [bit] NOT NULL DEFAULT 0,
    [CanDelete] [bit] NOT NULL DEFAULT 0,
    [CanExport] [bit] NOT NULL DEFAULT 0,
    [AdminActions] [bit] NOT NULL DEFAULT 0,
    [OtherActions] [bit] NOT NULL DEFAULT 0,
    [AssignedAt] [datetime] NOT NULL DEFAULT GETDATE(),
 CONSTRAINT [PK_RoleModules] PRIMARY KEY CLUSTERED ([RoleId] ASC, [ModuleId] ASC)
)
GO

-- =============================================
-- 8. Time Off System
-- =============================================
CREATE TABLE [dbo].[TimeOffRequests] (
    [RequestId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeOffRequests PRIMARY KEY,
    [EmployeeId] INT NOT NULL,
    [AbsenceType] VARCHAR(20) NOT NULL CHECK ([AbsenceType] IN ('vacation', 'personal', 'sick')),
    [Status] VARCHAR(20) NOT NULL DEFAULT ('pending') CHECK ([Status] IN ('pending', 'approved', 'rejected', 'cancelled')),
    [TimeUnit] VARCHAR(20) NOT NULL CHECK ([TimeUnit] IN ('full_day', 'half_day', 'hours')),
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
    [UpdatedAt] VARCHAR(19) NOT NULL
)
GO

CREATE TABLE [dbo].[TimeOffBalances] (
    [BalanceId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TimeOffBalances PRIMARY KEY,
    [EmployeeId] INT NOT NULL,
    [AbsenceType] VARCHAR(20) NOT NULL CHECK ([AbsenceType] IN ('vacation', 'personal', 'sick')),
    [Year] INT NOT NULL,
    [EntitledDays] VARCHAR(10) NOT NULL DEFAULT ('0.00'),
    [UsedDays] VARCHAR(10) NOT NULL DEFAULT ('0.00'),
    [PendingDays] VARCHAR(10) NOT NULL DEFAULT ('0.00'),
    [CarryoverDays] VARCHAR(10) NOT NULL DEFAULT ('0.00'),
    CONSTRAINT UQ_TimeOffBalances UNIQUE ([EmployeeId], [AbsenceType], [Year])
)
GO

CREATE TABLE [dbo].[Holidays] (
    [HolidayId] INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Holidays PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL,
    [Date] VARCHAR(10) NOT NULL UNIQUE,
    [Year] INT NOT NULL
)
GO

-- =============================================
-- 9. Foreign Keys Constraints
-- =============================================

-- Employees
ALTER TABLE [dbo].[Employees] WITH CHECK ADD CONSTRAINT [FK_Employees_Country] FOREIGN KEY([CountryId]) REFERENCES [dbo].[Countries] ([CountryId])
GO

-- EmployeeRoles
ALTER TABLE [dbo].[EmployeeRoles] WITH CHECK ADD CONSTRAINT [FK_EmployeeRoles_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[EmployeeRoles] WITH CHECK ADD CONSTRAINT [FK_EmployeeRoles_Roles] FOREIGN KEY([RoleId]) REFERENCES [dbo].[Roles] ([RoleId])
GO

-- TenantEmployees
ALTER TABLE [dbo].[TenantEmployees] WITH CHECK ADD CONSTRAINT [FK_TenantEmployees_Tenants] FOREIGN KEY([TenantId]) REFERENCES [dbo].[Tenants] ([TenantId])
GO
ALTER TABLE [dbo].[TenantEmployees] WITH CHECK ADD CONSTRAINT [FK_TenantEmployees_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO

-- Jobs / Curriculums / Licenses
ALTER TABLE [dbo].[Jobs] WITH CHECK ADD CONSTRAINT [FK_Jobs_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Jobs] WITH CHECK ADD CONSTRAINT [FK_Jobs_Country] FOREIGN KEY([CountryId]) REFERENCES [dbo].[Countries] ([CountryId])
GO
ALTER TABLE [dbo].[Curriculums] WITH CHECK ADD CONSTRAINT [FK_Curriculums_Jobs] FOREIGN KEY([JobId]) REFERENCES [dbo].[Jobs] ([JobId])
GO
ALTER TABLE [dbo].[Curriculums] WITH CHECK ADD CONSTRAINT [FK_Curriculums_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Licenses] WITH CHECK ADD CONSTRAINT [FK_Licenses_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO

-- Hardware Inventory
ALTER TABLE [dbo].[HardwareInventory] WITH CHECK ADD CONSTRAINT [FK_Hardware_Employees] FOREIGN KEY([EmployeeId]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO

-- Tickets
ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK_Tickets_CreatedBy_Employees] FOREIGN KEY([CreatedBy]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[Tickets] WITH CHECK ADD CONSTRAINT [FK_Tickets_AssignedTo_Employees] FOREIGN KEY([AssignedTo]) REFERENCES [dbo].[Employees] ([EmployeeId])
GO
ALTER TABLE [dbo].[ticketMessages] ADD CONSTRAINT FK_ticketMessages_Tickets FOREIGN KEY (TicketId) REFERENCES Tickets(TicketId)
GO
ALTER TABLE [dbo].[ticketMessages] ADD CONSTRAINT FK_ticketMessages_Employees FOREIGN KEY (UserId) REFERENCES Employees(EmployeeId)
GO
ALTER TABLE [dbo].[ticketAttachments] ADD CONSTRAINT FK_ticketAttachments_Tickets FOREIGN KEY (TicketId) REFERENCES Tickets(TicketId)
GO
ALTER TABLE [dbo].[ticketAttachments] ADD CONSTRAINT FK_ticketAttachments_TicketMessages FOREIGN KEY (TicketMessageId) REFERENCES ticketMessages(TicketMessageId)
GO

-- Modules
ALTER TABLE [dbo].[Modules] WITH CHECK ADD CONSTRAINT [FK_Modules_ParentModule] FOREIGN KEY([ParentModuleId]) REFERENCES [dbo].[Modules] ([ModuleId])
GO
ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK_RoleModules_Roles] FOREIGN KEY([RoleId]) REFERENCES [dbo].[Roles] ([RoleId]) ON DELETE CASCADE
GO
ALTER TABLE [dbo].[RoleModules] WITH CHECK ADD CONSTRAINT [FK_RoleModules_Modules] FOREIGN KEY([ModuleId]) REFERENCES [dbo].[Modules] ([ModuleId]) ON DELETE CASCADE
GO

-- TimeOff
ALTER TABLE [dbo].[TimeOffRequests] ADD CONSTRAINT FK_TimeOffRequests_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId])
GO
ALTER TABLE [dbo].[TimeOffRequests] ADD CONSTRAINT FK_TimeOffRequests_ReviewedBy FOREIGN KEY ([ReviewedBy]) REFERENCES [dbo].[Employees]([EmployeeId])
GO
ALTER TABLE [dbo].[TimeOffBalances] ADD CONSTRAINT FK_TimeOffBalances_Employee FOREIGN KEY ([EmployeeId]) REFERENCES [dbo].[Employees]([EmployeeId])
GO

-- =============================================
-- 10. Seed Data
-- =============================================

-- Countries
INSERT [dbo].[Countries] ([Name]) VALUES (N'USA'), (N'Mexico'), (N'Dominican Republic')
GO

-- Roles
INSERT [dbo].[Roles] ([RoleName], [Description]) VALUES 
(N'Admin', N'System Administrator'),
(N'Manager', N'Department Manager'),
(N'User', N'Standard User'),
(N'HR', N'Human Resources')
GO

-- Modules
SET IDENTITY_INSERT [dbo].[Modules] ON
INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard', N'dashboard', N'/dashboard', 1, 1, NULL),
       (2, N'Employees', N'employees', N'Employee management', N'people', N'/employees', 2, 1, NULL),
       (3, N'Jobs', N'jobs', N'Job postings', N'work', N'/jobs', 3, 1, NULL),
       (4, N'Curriculums', N'curriculums', N'CV management', N'description', N'/curriculums', 4, 1, NULL),
       (5, N'Licenses', N'licenses', N'License management', N'vpn_key', N'/licenses', 5, 1, NULL),
       (6, N'Administration', N'administration', N'Admin panel', N'settings', N'/administration', 6, 1, NULL),
       (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'/administration/roles', 1, 1, 6),
       (8, N'Permissions', N'permissions', N'Permissions', N'lock', N'/administration/permissions', 2, 1, 6),
       (9, N'Countries', N'countries', N'Countries', N'public', N'/administration/countries', 3, 1, 6)
SET IDENTITY_INSERT [dbo].[Modules] OFF
GO

-- RolePermissions (Admin gets all)
INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions]) 
SELECT 1, ModuleId, 1, 1, 1, 1, 1, 1 FROM [dbo].[Modules]
GO

PRINT 'External Database Initialized Successfully'
