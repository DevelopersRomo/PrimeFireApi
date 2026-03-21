USE [devromo]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-03-20 22:14:21 ******/
/****** Database: devromo on A2NWPLSK14SQL-v05.shr.prod.iad2.secureserver.net ******/
/****** This script contains ALL table structures and ALL data ******/

-- =============================================
-- DROP ALL TABLES
-- =============================================

IF OBJECT_ID('dbo.time_sheet_settings', 'U') IS NOT NULL
    DROP TABLE dbo.time_sheet_settings;
GO

IF OBJECT_ID('dbo.time_sheet_punches', 'U') IS NOT NULL
    DROP TABLE dbo.time_sheet_punches;
GO

IF OBJECT_ID('dbo.time_sheet_location_snapshots', 'U') IS NOT NULL
    DROP TABLE dbo.time_sheet_location_snapshots;
GO

IF OBJECT_ID('dbo.time_off_requests', 'U') IS NOT NULL
    DROP TABLE dbo.time_off_requests;
GO

IF OBJECT_ID('dbo.time_off_balances', 'U') IS NOT NULL
    DROP TABLE dbo.time_off_balances;
GO

IF OBJECT_ID('dbo.tickets', 'U') IS NOT NULL
    DROP TABLE dbo.tickets;
GO

IF OBJECT_ID('dbo.ticket_messages', 'U') IS NOT NULL
    DROP TABLE dbo.ticket_messages;
GO

IF OBJECT_ID('dbo.ticket_attachments', 'U') IS NOT NULL
    DROP TABLE dbo.ticket_attachments;
GO

IF OBJECT_ID('dbo.tenants', 'U') IS NOT NULL
    DROP TABLE dbo.tenants;
GO

IF OBJECT_ID('dbo.tenant_logos', 'U') IS NOT NULL
    DROP TABLE dbo.tenant_logos;
GO

IF OBJECT_ID('dbo.tenant_employees', 'U') IS NOT NULL
    DROP TABLE dbo.tenant_employees;
GO

IF OBJECT_ID('dbo.roles', 'U') IS NOT NULL
    DROP TABLE dbo.roles;
GO

IF OBJECT_ID('dbo.role_modules', 'U') IS NOT NULL
    DROP TABLE dbo.role_modules;
GO

IF OBJECT_ID('dbo.quotations', 'U') IS NOT NULL
    DROP TABLE dbo.quotations;
GO

IF OBJECT_ID('dbo.quotation_items', 'U') IS NOT NULL
    DROP TABLE dbo.quotation_items;
GO

IF OBJECT_ID('dbo.products', 'U') IS NOT NULL
    DROP TABLE dbo.products;
GO

IF OBJECT_ID('dbo.modules', 'U') IS NOT NULL
    DROP TABLE dbo.modules;
GO

IF OBJECT_ID('dbo.licenses', 'U') IS NOT NULL
    DROP TABLE dbo.licenses;
GO

IF OBJECT_ID('dbo.jobs', 'U') IS NOT NULL
    DROP TABLE dbo.jobs;
GO

IF OBJECT_ID('dbo.holidays', 'U') IS NOT NULL
    DROP TABLE dbo.holidays;
GO

IF OBJECT_ID('dbo.hardware_inventory', 'U') IS NOT NULL
    DROP TABLE dbo.hardware_inventory;
GO

IF OBJECT_ID('dbo.external_users', 'U') IS NOT NULL
    DROP TABLE dbo.external_users;
GO

IF OBJECT_ID('dbo.employees', 'U') IS NOT NULL
    DROP TABLE dbo.employees;
GO

IF OBJECT_ID('dbo.employee_roles', 'U') IS NOT NULL
    DROP TABLE dbo.employee_roles;
GO

IF OBJECT_ID('dbo.departments', 'U') IS NOT NULL
    DROP TABLE dbo.departments;
GO

IF OBJECT_ID('dbo.customers', 'U') IS NOT NULL
    DROP TABLE dbo.customers;
GO

IF OBJECT_ID('dbo.customer_notes', 'U') IS NOT NULL
    DROP TABLE dbo.customer_notes;
GO

IF OBJECT_ID('dbo.customer_attachments', 'U') IS NOT NULL
    DROP TABLE dbo.customer_attachments;
GO

IF OBJECT_ID('dbo.customer_alternate_contacts', 'U') IS NOT NULL
    DROP TABLE dbo.customer_alternate_contacts;
GO

IF OBJECT_ID('dbo.curriculums', 'U') IS NOT NULL
    DROP TABLE dbo.curriculums;
GO

IF OBJECT_ID('dbo.countries', 'U') IS NOT NULL
    DROP TABLE dbo.countries;
GO

IF OBJECT_ID('dbo.addresses', 'U') IS NOT NULL
    DROP TABLE dbo.addresses;
GO


-- =============================================
-- CREATE ALL TABLES
-- =============================================

-- =============================================
-- Table: addresses
-- =============================================

CREATE TABLE [dbo].[addresses](
    [address_id] [int] IDENTITY(1,1) NOT NULL,
    [address_1] [nvarchar](200) NOT NULL,
    [address_2] [nvarchar](200) NULL,
    [city] [nvarchar](100) NOT NULL,
    [state] [nvarchar](100) NOT NULL,
    [zip_code] [nvarchar](20) NOT NULL,
    [country_id] [int] NOT NULL,
    [google_place_id] [nvarchar](255) NULL,
    [is_validated] [bit] NOT NULL DEFAULT ((0)),
    [validated_at] [datetime2] NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
 CONSTRAINT [pk_addresses] PRIMARY KEY CLUSTERED
(
    [address_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: countries
-- =============================================

CREATE TABLE [dbo].[countries](
    [country_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [varchar](20) NULL,
 CONSTRAINT [pk_countrie_10d1609f78e422f4] PRIMARY KEY CLUSTERED
(
    [country_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: curriculums
-- =============================================

CREATE TABLE [dbo].[curriculums](
    [curriculum_id] [int] IDENTITY(1,1) NOT NULL,
    [job_id] [int] NOT NULL,
    [name] [varchar](100) NOT NULL,
    [email] [varchar](100) NOT NULL,
    [phone] [varchar](20) NULL,
    [curriculum_path] [varchar](255) NULL,
    [cover_letter] [varchar](1000) NULL,
    [status] [varchar](20) NOT NULL,
    [submitted_at] [datetime] NOT NULL,
    [employee_id] [int] NULL,
 CONSTRAINT [pk_curricul_06c9fa1c1a1b5187] PRIMARY KEY CLUSTERED
(
    [curriculum_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: customer_alternate_contacts
-- =============================================

CREATE TABLE [dbo].[customer_alternate_contacts](
    [customer_alternate_contact_id] [int] IDENTITY(1,1) NOT NULL,
    [customer_id] [int] NOT NULL,
    [name] [nvarchar](200) NOT NULL,
    [email] [nvarchar](255) NULL,
    [phone] [nvarchar](20) NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [updated_at] [datetime2] NULL,
 CONSTRAINT [pk_customer_alternate_contacts] PRIMARY KEY CLUSTERED
(
    [customer_alternate_contact_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: customer_attachments
-- =============================================

CREATE TABLE [dbo].[customer_attachments](
    [customer_attachment_id] [int] IDENTITY(1,1) NOT NULL,
    [customer_id] [int] NOT NULL,
    [file_name] [nvarchar](255) NOT NULL,
    [file_type] [nvarchar](100) NULL,
    [file_path] [nvarchar](500) NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [created_by] [int] NOT NULL,
 CONSTRAINT [pk_customer_attachments] PRIMARY KEY CLUSTERED
(
    [customer_attachment_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: customer_notes
-- =============================================

CREATE TABLE [dbo].[customer_notes](
    [customer_note_id] [int] IDENTITY(1,1) NOT NULL,
    [customer_id] [int] NOT NULL,
    [note_text] [nvarchar](MAX) NOT NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [updated_at] [datetime2] NULL,
    [created_by] [int] NOT NULL,
 CONSTRAINT [pk_customer_notes] PRIMARY KEY CLUSTERED
(
    [customer_note_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: customers
-- =============================================

CREATE TABLE [dbo].[customers](
    [customer_id] [int] IDENTITY(1,1) NOT NULL,
    [customer_type] [nvarchar](20) NOT NULL,
    [company_name] [nvarchar](200) NULL,
    [first_name] [nvarchar](100) NULL,
    [last_name] [nvarchar](100) NULL,
    [additional_name] [nvarchar](100) NULL,
    [market] [nvarchar](50) NULL,
    [dtd_potential] [nvarchar](20) NULL,
    [primary_email] [nvarchar](255) NULL,
    [primary_phone] [nvarchar](20) NULL,
    [primary_address_id] [int] NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [updated_at] [datetime2] NULL,
    [created_by] [int] NOT NULL,
 CONSTRAINT [pk_customers] PRIMARY KEY CLUSTERED
(
    [customer_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: departments
-- =============================================

CREATE TABLE [dbo].[departments](
    [department_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [nvarchar](100) NOT NULL,
    [code] [nvarchar](20) NULL,
 CONSTRAINT [pk_departments] PRIMARY KEY CLUSTERED
(
    [department_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: employee_roles
-- =============================================

CREATE TABLE [dbo].[employee_roles](
    [employee_id] [int] NOT NULL,
    [role_id] [int] NOT NULL,
 CONSTRAINT [pk_employee_c27fe3f0c0f63c02] PRIMARY KEY CLUSTERED
(
    [employee_id] ASC,[role_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: employees
-- =============================================

CREATE TABLE [dbo].[employees](
    [employee_id] [int] IDENTITY(1,1) NOT NULL,
    [first_name] [varchar](50) NULL,
    [last_name] [varchar](50) NULL,
    [display_name] [varchar](100) NULL,
    [title] [varchar](50) NULL,
    [department] [varchar](50) NULL,
    [office] [varchar](50) NULL,
    [email] [varchar](50) NULL,
    [phone] [varchar](20) NULL,
    [mobile_phone] [varchar](20) NULL,
    [office_phone] [varchar](20) NULL,
    [street_address] [varchar](100) NULL,
    [city] [varchar](50) NULL,
    [state] [varchar](50) NULL,
    [postal_code] [varchar](20) NULL,
    [country_id] [int] NULL,
    [azure_oid] [varchar](100) NULL,
    [azure_upn] [varchar](100) NULL,
    [last_synced_at] [datetime] NULL,
    [anydesk] [nvarchar](50) NULL,
    [password_hash] [nvarchar](255) NULL,
    [manager] [nvarchar](100) NULL,
    [manager_email] [nvarchar](100) NULL,
    [manager_employee_id] [int] NULL,
 CONSTRAINT [pk_employee_7ad04f1160241b26] PRIMARY KEY CLUSTERED
(
    [employee_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: external_users
-- =============================================

CREATE TABLE [dbo].[external_users](
    [external_user_id] [int] IDENTITY(1,1) NOT NULL,
    [email] [varchar](100) NOT NULL,
    [password_hash] [varchar](255) NOT NULL,
    [tenant_id] [int] NOT NULL,
    [created_at] [datetime] NOT NULL,
 CONSTRAINT [pk_external_94cc235758f0bdbe] PRIMARY KEY CLUSTERED
(
    [external_user_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: hardware_inventory
-- =============================================

CREATE TABLE [dbo].[hardware_inventory](
    [hardware_id] [int] IDENTITY(1,1) NOT NULL,
    [serial_number] [varchar](50) NOT NULL,
    [brand] [varchar](50) NOT NULL,
    [model] [varchar](100) NULL,
    [device_type] [varchar](20) NULL,
    [processor] [varchar](100) NULL,
    [ram_gb] [int] NULL,
    [storage_type] [varchar](20) NULL,
    [storage_size_gb] [int] NULL,
    [gpu] [varchar](100) NULL,
    [operating_system] [varchar](100) NULL,
    [warranty_start_date] [date] NULL,
    [warranty_end_date] [date] NULL,
    [purchase_date] [date] NULL,
    [employee_id] [int] NULL,
    [location] [varchar](100) NULL,
    [status] [varchar](20) NULL,
    [notes] [varchar](255) NULL,
    [created_at] [datetime] NULL,
    [updated_at] [datetime] NULL,
 CONSTRAINT [pk_hardware_13a9b58868586958] PRIMARY KEY CLUSTERED
(
    [hardware_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: holidays
-- =============================================

CREATE TABLE [dbo].[holidays](
    [holiday_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [nvarchar](100) NOT NULL,
    [date] [varchar](10) NOT NULL,
    [year] [int] NOT NULL,
 CONSTRAINT [pk_holidays] PRIMARY KEY CLUSTERED
(
    [holiday_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: jobs
-- =============================================

CREATE TABLE [dbo].[jobs](
    [job_id] [int] IDENTITY(1,1) NOT NULL,
    [title] [varchar](100) NOT NULL,
    [description] [varchar](1000) NULL,
    [requirements] [varchar](1000) NULL,
    [location] [varchar](100) NULL,
    [salary_min] [float] NULL,
    [salary_max] [float] NULL,
    [status] [varchar](20) NOT NULL,
    [posted_at] [datetime] NOT NULL,
    [employee_id] [int] NULL,
    [country_id] [int] NULL,
 CONSTRAINT [pk_jobs_056690c2c3a32b63] PRIMARY KEY CLUSTERED
(
    [job_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: licenses
-- =============================================

CREATE TABLE [dbo].[licenses](
    [license_id] [int] IDENTITY(1,1) NOT NULL,
    [software] [varchar](50) NULL,
    [version] [varchar](20) NULL,
    [created_at] [date] NULL,
    [expiry_date] [date] NULL,
    [key] [varchar](50) NULL,
    [account] [varchar](50) NULL,
    [Password] [varchar](50) NULL,
    [employee_id] [int] NULL,
    [notes] [nvarchar](500) NULL,
 CONSTRAINT [pk_licenses_72d6008283025401] PRIMARY KEY CLUSTERED
(
    [license_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: modules
-- =============================================

CREATE TABLE [dbo].[modules](
    [module_id] [int] IDENTITY(1,1) NOT NULL,
    [module_name] [varchar](50) NOT NULL,
    [module_key] [varchar](50) NOT NULL,
    [description] [varchar](200) NULL,
    [icon] [varchar](50) NULL,
    [route_url] [varchar](100) NULL,
    [display_order] [int] NULL,
    [is_active] [bit] NOT NULL,
    [parent_module_id] [int] NULL,
    [created_at] [datetime] NULL,
 CONSTRAINT [pk_modules_2b7477a770a3bb13] PRIMARY KEY CLUSTERED
(
    [module_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: products
-- =============================================

CREATE TABLE [dbo].[products](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [name] [nvarchar](200) NOT NULL,
    [description] [nvarchar](2000) NULL,
    [type] [varchar](20) NOT NULL,
    [sku] [nvarchar](100) NULL,
    [unit_price] [numeric](18,2) NOT NULL DEFAULT ((0)),
    [cost] [numeric](18,2) NOT NULL DEFAULT ((0)),
    [tax_rate] [numeric](5,2) NOT NULL DEFAULT ((0)),
    [unit] [nvarchar](50) NOT NULL DEFAULT ('pieza'),
    [stock_quantity] [int] NOT NULL DEFAULT ((0)),
    [is_active] [bit] NOT NULL DEFAULT ((1)),
    [created_at] [datetime2] NOT NULL DEFAULT (sysdatetime()),
 CONSTRAINT [pk_products_3214ec07aaf87c3c] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: quotation_items
-- =============================================

CREATE TABLE [dbo].[quotation_items](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [quotation_id] [int] NOT NULL,
    [product_id] [int] NOT NULL,
    [description] [nvarchar](1000) NULL,
    [quantity] [decimal](18,2) NOT NULL DEFAULT ((1)),
    [unit_price] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [total] [decimal](18,2) NOT NULL DEFAULT ((0)),
 CONSTRAINT [pk_quotatio_3214ec0771223114] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: quotations
-- =============================================

CREATE TABLE [dbo].[quotations](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [customer_id] [int] NOT NULL,
    [quote_date] [datetime2] NOT NULL DEFAULT (sysdatetime()),
    [expiration_date] [datetime2] NULL,
    [subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [status] [varchar](20) NOT NULL DEFAULT ('Draft'),
    [notes] [nvarchar](2000) NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysdatetime()),
 CONSTRAINT [pk_quotatio_3214ec07ab66981d] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: role_modules
-- =============================================

CREATE TABLE [dbo].[role_modules](
    [role_id] [int] NOT NULL,
    [module_id] [int] NOT NULL,
    [CanView] [bit] NOT NULL,
    [CanCreate] [bit] NOT NULL,
    [CanEdit] [bit] NOT NULL,
    [CanDelete] [bit] NOT NULL,
    [CanExport] [bit] NOT NULL,
    [AdminActions] [bit] NOT NULL,
    [OtherActions] [bit] NOT NULL,
    [AssignedAt] [datetime] NULL,
 CONSTRAINT [pk_role_modu_e84d89600a5756de] PRIMARY KEY CLUSTERED
(
    [role_id] ASC,[module_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: roles
-- =============================================

CREATE TABLE [dbo].[roles](
    [role_id] [int] IDENTITY(1,1) NOT NULL,
    [role_name] [varchar](50) NOT NULL,
    [description] [varchar](200) NULL,
 CONSTRAINT [pk_roles_8aface1a81a168c1] PRIMARY KEY CLUSTERED
(
    [role_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: tenant_employees
-- =============================================

CREATE TABLE [dbo].[tenant_employees](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [tenant_id] [int] NULL,
    [created_at] [datetime] NOT NULL,
    [email] [nvarchar](100) NULL,
    [password_hash] [nvarchar](255) NULL,
 CONSTRAINT [pk_tenant_em_3214ec072433eafd] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: tenant_logos
-- =============================================

CREATE TABLE [dbo].[tenant_logos](
    [logo_id] [int] IDENTITY(1,1) NOT NULL,
    [tenant_id] [int] NOT NULL,
    [title] [varchar](100) NOT NULL,
    [description] [varchar](500) NULL,
    [path] [varchar](500) NOT NULL,
    [path_background] [varchar](500) NULL,
    [primary_color] [varchar](50) NULL,
    [secondary_color] [varchar](50) NULL,
    [tertiary_color] [varchar](50) NULL,
    [created_at] [datetime] NOT NULL,
    [updated_at] [datetime] NULL,
    [url] [nvarchar](500) NOT NULL,
    [fav_icon] [nvarchar](500) NULL,
    [email] [nvarchar](255) NULL,
 CONSTRAINT [pk_tenant_lo_c620158d40bfcf43] PRIMARY KEY CLUSTERED
(
    [logo_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: tenants
-- =============================================

CREATE TABLE [dbo].[tenants](
    [tenant_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [varchar](100) NOT NULL,
    [db_connection_key] [varchar](50) NOT NULL,
    [description] [varchar](255) NULL,
    [is_active] [bit] NOT NULL,
    [created_at] [datetime] NOT NULL,
 CONSTRAINT [pk_tenants_2e9b47e1f92eb300] PRIMARY KEY CLUSTERED
(
    [tenant_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: ticket_attachments
-- =============================================

CREATE TABLE [dbo].[ticket_attachments](
    [ticket_attachment_id] [int] IDENTITY(1,1) NOT NULL,
    [ticket_id] [int] NOT NULL,
    [ticket_message_id] [int] NULL,
    [file_name] [varchar](255) NOT NULL,
    [file_type] [varchar](100) NULL,
    [file_path] [varchar](500) NULL,
    [created_at] [datetime] NOT NULL,
 CONSTRAINT [pk_ticket_at_25528bc8235cc48c] PRIMARY KEY CLUSTERED
(
    [ticket_attachment_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: ticket_messages
-- =============================================

CREATE TABLE [dbo].[ticket_messages](
    [ticket_message_id] [int] IDENTITY(1,1) NOT NULL,
    [ticket_id] [int] NOT NULL,
    [user_id] [int] NOT NULL,
    [message_txt] [varchar](MAX) NULL,
    [created_at] [datetime] NOT NULL,
    [updated_at] [datetime] NULL,
    [edited_at] [datetime] NULL,
 CONSTRAINT [pk_ticket_me_602a18a4d77f2994] PRIMARY KEY CLUSTERED
(
    [ticket_message_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: tickets
-- =============================================

CREATE TABLE [dbo].[tickets](
    [ticket_id] [int] IDENTITY(1,1) NOT NULL,
    [title] [varchar](200) NOT NULL,
    [description] [varchar](2000) NULL,
    [status] [varchar](11) NOT NULL,
    [priority] [varchar](6) NOT NULL,
    [sla] [varchar](3) NULL,
    [created_by] [int] NOT NULL,
    [assigned_to] [int] NULL,
    [created_at] [datetime] NOT NULL,
    [updated_at] [datetime] NOT NULL,
 CONSTRAINT [pk_tickets_712cc607abd622ab] PRIMARY KEY CLUSTERED
(
    [ticket_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: time_off_balances
-- =============================================

CREATE TABLE [dbo].[time_off_balances](
    [balance_id] [int] IDENTITY(1,1) NOT NULL,
    [employee_id] [int] NOT NULL,
    [absence_type] [varchar](20) NOT NULL,
    [year] [int] NOT NULL,
    [entitled_days] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [used_days] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [pending_days] [varchar](10) NOT NULL DEFAULT ('0.00'),
    [carryover_days] [varchar](10) NOT NULL DEFAULT ('0.00'),
 CONSTRAINT [pk_time_off_balances] PRIMARY KEY CLUSTERED
(
    [balance_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: time_off_requests
-- =============================================

CREATE TABLE [dbo].[time_off_requests](
    [request_id] [int] IDENTITY(1,1) NOT NULL,
    [employee_id] [int] NOT NULL,
    [absence_type] [varchar](20) NOT NULL,
    [status] [varchar](20) NOT NULL DEFAULT ('pending'),
    [time_unit] [varchar](20) NOT NULL,
    [start_date] [varchar](10) NOT NULL,
    [end_date] [varchar](10) NOT NULL,
    [start_time] [varchar](8) NULL,
    [end_time] [varchar](8) NULL,
    [total_hours] [varchar](10) NULL,
    [total_days] [varchar](10) NOT NULL,
    [reason] [nvarchar](MAX) NULL,
    [reviewed_by] [int] NULL,
    [reviewed_at] [varchar](19) NULL,
    [review_notes] [nvarchar](MAX) NULL,
    [created_at] [varchar](19) NOT NULL,
    [updated_at] [varchar](19) NOT NULL,
 CONSTRAINT [pk_time_off_requests] PRIMARY KEY CLUSTERED
(
    [request_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: time_sheet_location_snapshots
-- =============================================

CREATE TABLE [dbo].[time_sheet_location_snapshots](
    [snapshot_id] [int] IDENTITY(1,1) NOT NULL,
    [employee_id] [int] NOT NULL,
    [customer_id] [int] NULL,
    [ip_address] [varchar](45) NULL,
    [latitude] [varchar](20) NULL,
    [longitude] [varchar](20) NULL,
    [gps_accuracy] [varchar](20) NULL,
    [city] [varchar](100) NULL,
    [region] [varchar](100) NULL,
    [country] [varchar](100) NULL,
    [timezone] [varchar](80) NULL,
    [location_raw] [varchar](MAX) NULL,
    [captured_at] [varchar](19) NOT NULL,
 CONSTRAINT [pk_time_shee_664f572b28fa444d] PRIMARY KEY CLUSTERED
(
    [snapshot_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: time_sheet_punches
-- =============================================

CREATE TABLE [dbo].[time_sheet_punches](
    [punch_id] [int] IDENTITY(1,1) NOT NULL,
    [employee_id] [int] NOT NULL,
    [customer_id] [int] NOT NULL,
    [clock_in_at] [varchar](19) NOT NULL,
    [clock_out_at] [varchar](19) NULL,
    [timezone] [varchar](80) NULL,
    [ip_address] [varchar](45) NULL,
    [latitude] [varchar](20) NULL,
    [longitude] [varchar](20) NULL,
    [gps_accuracy] [varchar](20) NULL,
    [city] [varchar](100) NULL,
    [region] [varchar](100) NULL,
    [country] [varchar](100) NULL,
    [location_raw] [varchar](MAX) NULL,
    [worked_minutes] [int] NOT NULL,
    [status] [varchar](20) NOT NULL,
    [Note] [varchar](2000) NULL,
    [approved_by] [int] NULL,
    [approved_at] [varchar](19) NULL,
    [created_at] [varchar](19) NOT NULL,
    [updated_at] [varchar](19) NOT NULL,
 CONSTRAINT [pk_time_shee_f6292c23063fbf56] PRIMARY KEY CLUSTERED
(
    [punch_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: time_sheet_settings
-- =============================================

CREATE TABLE [dbo].[time_sheet_settings](
    [setting_id] [int] IDENTITY(1,1) NOT NULL,
    [overtime_daily_hours] [varchar](10) NOT NULL,
    [overtime_weekly_hours] [varchar](10) NULL,
    [round_to_minutes] [int] NULL,
    [is_active] [bit] NOT NULL,
    [created_at] [varchar](19) NOT NULL,
    [updated_at] [varchar](19) NOT NULL,
    [max_overtime_daily_hours] [nvarchar](10) NULL,
 CONSTRAINT [pk_time_shee_54372b1d995bd25a] PRIMARY KEY CLUSTERED
(
    [setting_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


-- =============================================
-- INSERT DATA FOR ALL TABLES
-- =============================================


-- Data for countries (5 records)
SET IDENTITY_INSERT [dbo].[countries] ON
GO

INSERT [dbo].[countries] ([country_id], [name]) VALUES (1, N'US')
INSERT [dbo].[countries] ([country_id], [name]) VALUES (2, N'PR')
INSERT [dbo].[countries] ([country_id], [name]) VALUES (3, N'DO')
INSERT [dbo].[countries] ([country_id], [name]) VALUES (4, N'MX')
INSERT [dbo].[countries] ([country_id], [name]) VALUES (5, N'Mexico')

SET IDENTITY_INSERT [dbo].[countries] OFF
GO


-- Data for addresses (7 records)
SET IDENTITY_INSERT [dbo].[addresses] ON
GO

INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (1, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, '2026-02-01 02:00:09')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (2, N'Highway 8860 Km 1.2. Camino Matienzo Cintrón', NULL, N'Trujillo Alto,', N'Puerto Rico', N'00977', 1, NULL, 0, NULL, '2026-02-06 00:14:22')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (3, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, '2026-02-23 23:49:35')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (4, N'Highway 8860 Km 1.2', NULL, N'Trujillo Alto', N'PR', N'00977', 2, NULL, 0, NULL, '2026-02-23 23:52:39')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (5, N'10670 N Central Expy', NULL, N'Dallas', N'Texas', N'75231', 1, NULL, 0, NULL, '2026-02-23 23:57:15')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (6, N'N Henderson ave suite #308', NULL, N'Dallas', N'75206', N'75206', 1, NULL, 0, NULL, '2026-02-24 00:02:52')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (7, N'Office', NULL, N'Dallas', N'TX', N'75224', 1, NULL, 0, NULL, '2026-02-24 00:09:21')

SET IDENTITY_INSERT [dbo].[addresses] OFF
GO


-- curriculums: No data to insert


-- Data for employees (50 records)
SET IDENTITY_INSERT [dbo].[employees] ON
GO

INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (1, N'Juan', N'Carlos', N'Juan Carlos', N'Developer', N'IT', N'MX', N'jcarlos.villa.rivera@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'292367b5-7d70-4d13-81cb-ee6f7c650275', NULL, NULL, NULL, N'$2b$12$86/wa5zSinRGMtad4BiNrO77K9zNAUPRTpQl3KtGABf6/E3LqS5hq', NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (2, N'Jonathan', N'Romo', N'Jonathan Romo', N'External User', N'IT', N'MTY', N'info@devromo.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'08a89d51-b7c7-404a-9d2b-ee9f7440d63c', NULL, NULL, NULL, N'$2b$12$Zq0QadTdL/6ESgImpwBxT.zKkVns1Wrqrj8W9LkKrSxYRHoEswynC', N'jony.romo001', N'jony_romo@hotmail.com', 142)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (142, N'Eli', N'Romo', N'jony.romo001', N'External User', NULL, NULL, N'jony_romo@hotmail.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'7dffa13b-fe6f-4406-b429-93694b40284e', NULL, NULL, NULL, N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG', N'Jonathan Romo', N'info@devromo.com', 2)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (143, N'Adolfo', N'Martinez', N'Adolfo Martinez', N'Manager Alarm Designer', N'Engineering Alarms', N'Home Office TX', N'amartinez@primefire.us', NULL, N'+1 4075584334', N'+1 4075584334', N'Dallas, TX', N'Dallas', N'Texas (TX)', N'75202', 1, N'1e7152f1-aaf5-4789-9da4-e74d9b586843', N'amartinez@primefire.us', '2026-03-13 00:46:39', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (144, N'Jose Alberto', N'Rodriguez', N'Jose Alberto Rodriguez', N'President & CEO', N'President', N'Trujillo Alto, Puerto Rico', N'arodriguez@primefire.us', NULL, N'+1 7872212121', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b826abb3-30c8-4369-8d87-ce0d648e7fba', N'arodriguez@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (145, N'Baxter', N'Jayuya', N'Baxter Jayuya', N'Engineering Alarm', N'Engineering Alarm Designer', N'Guaynabo, Puerto Rico', N'bjayuya@primefire.us', NULL, NULL, N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'b9de2f69-4aba-42f3-87eb-da0e1dcf2cfa', N'bjayuya@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (146, N'Christopher', N'Carballo Rosado', N'Christopher Carballo Rosado', N'Fire Alarm Manager', N'Alarm Project Manager', N'Guaynabo, Puerto Rico', N'ccarballo@primefire.us', NULL, N'+1 7872017346', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'd63e397b-31e7-424e-a2c3-993562347b04', N'ccarballo@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (147, N'Cesar', N'Figueroa Cruzado', N'Cesar Figueroa Cruzado', N'Group Leader', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'cfigueroa@primefire.us', NULL, N'+1 9398919203 ', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', NULL, N'b5ff98b3-be60-4693-aa6e-2553b941faff', N'cfigueroa@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (148, N'Jose Daniel', N'Agosto Rivera', N'Jose Daniel Agosto Rivera', NULL, NULL, NULL, N'dagosto@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'a5c57db5-230b-41c2-a0e7-0747f4512d2d', N'dagosto@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (149, NULL, NULL, N'Dominicana', NULL, NULL, NULL, N'dominicana@primefire.do', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'405c6850-50aa-490a-91f0-b666e016f12e', N'dominicana@primefire.do', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (150, N'Edwin', N'De Jesus', N'Edwin De Jesus', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'edejesus@primefire.us', NULL, N'+1 7876433660', N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1efe087c-1bd7-4e77-9ec3-5577519a9871', N'edejesus@primefire.us', '2026-03-13 00:46:40', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (151, N'Emmanuel', N'Desueza', N'Enmanuel Desueza', N'Project Coordinator', N'Field Technician, Office Assistant ', N'Santo Domingo, República Dominicana', N'edesueza@primefire.do', NULL, N'+1 8095011901', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'b0241d3b-03a7-45bf-a2fa-f06a76b9317d', N'edesueza@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (152, N'Edwin', N'Guilloty', N'Edwin Guilloty', N'Project Manager', N'Operations', N'Guaynabo, Puerto Rico', N'eguilloty@primefire.us', NULL, N'+1 7876433660', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'76025b90-b5a8-4ba7-809b-0da6685492f8', N'eguilloty@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (153, N'Elizaud', N'Hernandez', N'Elizaud Hernandez', N'Administration Manager', N'Administration', N'Trujillo Alto, Puerto Rico', N'ehernandez@primefire.us', NULL, N'+1 3867483621', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'ad15e516-906b-4e3f-8e4c-373134505755', N'ehernandez@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (154, N'Emilio', N'Melendez', N'Emilio Melendez', N'Field Tech', N'Logistics / Operations', N'Prime Fire DO', N'emelendez@primefire.do', NULL, NULL, NULL, N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominiaca', N'10109', 3, N'4c12442f-758b-4921-8188-b0167d3e6281', N'emelendez@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (155, N'Elionetzy', N'Santiago Adames', N'Elionetzy Santiago Adames', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto', N'esadames@primefire.us', NULL, N'+1 7874729866', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b892a33-b52b-4f24-9af1-941c3eceb183', N'esadames@primefire.us', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (156, N'Gustavo', N'Heredia', N'Gustavo Heredia', N'Designer ', NULL, NULL, N'gheredia@primefire.do', NULL, N'+1 8492854334', NULL, N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'44d8c9a2-c02f-41c7-85e0-50c9f92ec327', N'gheredia@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (157, N'Geurys Jabbart', N'Medrano Montero', N'Geurys Medrano', N'Global Inventory Manager', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'gmedrano@primefire.do', NULL, N'+1 8295594355', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6dc58092-0b27-431c-a2b6-353e2fcf4c49', N'gmedrano@primefire.do', '2026-03-13 00:46:41', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (158, N'Gustavo', N'Vazquez', N'Gustavo Vazquez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvazquez@primefire.us', NULL, N'1 (787) 312-7679', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'07e0c48e-bc49-4f58-9e3b-c391b4fe12c2', N'gvazquez@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (159, N'Giovanni', N'Velez', N'Giovanni Velez', N'Fire Alarm Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvelez@primefire.us', NULL, N'+1 7873700568', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8b6db431-ee49-46c2-be9a-2e89a493130a', N'gvelez@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (160, NULL, NULL, N'Info', NULL, NULL, NULL, N'info@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'53172d9b-ad7e-49e4-81ce-25c1c7656a3e', N'info@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (161, N'Israel', N'Nieves', N'Israel Nieves', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto, Puerto Rico', N'inieves@primefire.us', NULL, N'+1 7872047807', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'396751cd-b9ac-40e9-8122-dffb9341f319', N'inieves@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (162, N'Jonathan', N'Romo', N'Jonathan Romo', N'Admin Systems', N'IT', N'Home Office, Mexico', N'it@primefire.us', NULL, N'+528125356287', N'+528125356287', N'Arturo B de la Garza #4613', N'Monterrey', NULL, NULL, 4, N'8c882f2c-19f8-4f17-a1e8-d5644456ea65', N'it@primefire.us', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (163, N'Juan', N'Aybar', N'Juan Lehtenin', N'Fire Alarm Division', N'PrimeFire DO', N'República Dominica', N'jaybar@primefire.do', NULL, NULL, N'+1 8095011901', N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominicana', N'10109', 3, N'2a9640a5-897f-49c0-94f7-15a6f4d642c9', N'jaybar@primefire.do', '2026-03-13 00:46:42', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (164, N'Joskayra', N'de Jesus Medina', N'Joskayra de Jesus Medina', N'Engineering Alarm Designer & Accountant', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'jdejesus@primefire.do', NULL, N'+1 809-499-5821', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'df97493e-56d4-45fb-8a18-25a60dead4b5', N'jdejesus@primefire.do', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (165, N'Javier', N'Lopez Rivera', N'Javier Lopez Rivera', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jlopez@primefire.us', NULL, N'+1 9393399185', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'e809702b-2fb2-45d3-b486-04f66b89d725', N'jlopez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (166, N'Jose', N'Martínez', N'Jose Martínez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jmartinez@primefire.us', NULL, N'+1 787-948-3352', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1eb06cab-eeae-425b-bd0e-562d6eb89735', N'jmartinez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (167, N'Jose', N'Morales', N'Jose Morales', N'Group Leader', N'Sprinklers Division', N'Trujillo Alto, Puerto Rico', N'jmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'd96be71d-b61f-40e5-b973-94843acf7c47', N'jmorales@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (168, N'Juan', N'Villa', N'Juan Villa', N'Systems', N'IT', N'Home Office, Mexico', N'jvilla@primefire.us', NULL, N'+522282553841', N'+522282553841', N'Retorno Pantochica #3', N'Xalapa', N'Veracruz', N'91098', 4, N'0523631c-d286-4be5-9aaf-e33ac83b587c', N'jvilla@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (169, N'Kevin', N'Lopez', N'Kevin Lopez', NULL, NULL, NULL, N'klopez@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'ac51c4f9-269a-44a8-99b9-aae4220a7e4e', N'klopez@primefire.us', '2026-03-13 00:46:43', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (170, N'Kevin', N'Morales', N'Kevin Morales', N'Administrative Assistant', N'HR Analyst', N'Trujillo Alto, Puerto Rico', N'kmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b7ae779-a20d-47d9-9680-ccf54568ae41', N'kmorales@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (171, N'Kristian', N'Torres', N'Kristian Torres', N'Field Tech', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ktorres@primefire.us', NULL, N'+1 4077059670', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'b02a129b-cb1f-4d22-ab12-acbbeb5291e2', N'ktorres@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (172, N'Luis', N'Belliard', N'Luis Belliard', N'Fire Sprinklers Designer', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'lbelliard@primefire.do', NULL, N'+1 8292222869', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6e029e87-b520-4def-8aed-9484162bee13', N'lbelliard@primefire.do', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (173, N'Luis', N'Burset', N'Luis Burset', N'Fire Sprinklers Designer', N'Designer', N'Home Office TX', N'lburset@primefire.us', NULL, N'+1 7874855008', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR', N'00976', 2, N'88b8d661-148d-4476-881c-d42f4d3ef96e', N'lburset@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (174, N'Luis', N'De Jesus', N'Luis De Jesus', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ldejesus@primefire.us', NULL, N'+1 7873909755', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8d91aafe-6b6d-4994-84d4-5108e4e7b0ca', N'ldejesus@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (175, N'Luis D', N'Lugo', N'Luis D Lugo', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'llugo@primefire.us', NULL, N'+1 7879514104', N'+1 7876306000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'542a5a99-aa6a-4ce9-8435-e42f587444b6', N'llugo@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (176, N'Luis', N'Nieves', N'Luis Nieves', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'lnieves@primefire.us', NULL, N'+1 7873641643', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'8f082fd0-cad1-4579-8305-08b31f95befd', N'lnieves@primefire.us', '2026-03-13 00:46:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (177, N'Max', N'Oliveras', N'Max Oliveras', N'Project Manager', N'Field Engineering', N'Trujillo Alto', N'moliveras@primefire.us', NULL, N'+ 787 607 7402', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'41b65f97-f746-46c2-b03a-9f0dffaefb19', N'moliveras@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (178, N'Marcos', N'Quiles', N'Marcos Quiles', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'mquiles@primefire.us', NULL, N'+1 7875257965', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'0f46165b-1617-4d70-82f4-f4768b01f90c', N'mquiles@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (179, N'Nathan', N'Gonzalez', N'Nathan Gonzalez', N'Engineering Alarm Designers', N'Engineering Alarm', N'Trujillo Alto, Puerto Rico', N'ngonzalez@primefire.us', NULL, N'+1 7879819444', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'c9d2250f-2b79-403f-9c13-fe11212f4ebb', N'ngonzalez@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (180, NULL, NULL, N'Printer Guaynabo', NULL, NULL, NULL, N'Printer-Guaynabo@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'5719f4d2-8092-48f8-a53a-d6f0e28bf8ea', N'Printer-Guaynabo@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (181, N'Rayneé', N'Fúnez Heredia', N'Rayneé Fúnez Heredia', N'Account Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'rfunez@primefire.us', NULL, N'+1 9392350216', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'ab01cd10-bff4-4620-b55e-0d0f1ab1d151', N'rfunez@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (182, N'Rosa M', N'Rivera', N'Rosa M Rivera', N'Project Manager - Ai Strategic Efficiency', N'Administration', N'Guaynabo', N'rmrivera@primefire.us', NULL, N'(787)975-9127', N'787-630-6000', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'aa1aafd1-f175-4595-9dc1-d018b8069d66', N'rmrivera@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (183, N'Rolando', N'Rivera', N'Rolando Rivera', N'Alarm Designer', NULL, N'Guaynabo, Puerto Rico', N'rrivera@primefire.us', NULL, N'+1 7872377217', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'706337f9-ef71-47cb-982f-2ca206383da3', N'rrivera@primefire.us', '2026-03-13 00:46:45', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (184, N'Sigfredo', N'Carrero', N'Sigfredo Carrero', N'General Manager / Sprinkler Division', N'SubDirection', N'Trujillo Alto, Puerto Rico', N'scarrero@primefire.us', NULL, N'+1 7876475955', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b7d6932d-8c4c-411f-ab87-1547f9c07391', N'scarrero@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (185, NULL, NULL, N'service', NULL, NULL, NULL, N'service@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'f1228614-b6eb-4c3e-bbae-869139b6736e', N'service@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (186, N'Stephanie', N'Martinez', N'Stephanie Martinez', N'HR Analyst', N'Hiuman Resource', N'Trujillo Alto, Puerto Rico', N'smartinez@primefire.us', NULL, N'+1 8292485211', N'+1 8095011901', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'9cfcf921-1266-468c-a7de-0ee20fd472cb', N'smartinez@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (187, N'Santiago', N'Rodriguez', N'Santiago Rodriguez', N'Operation Manager', N'Field Engineering ', N'Santo Domingo, República Dominicana', N'srodriguez@primefire.do', NULL, N'+1 7876077402', N'+1 7877613180', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'635af9c2-ca37-4e5a-bfdd-989e0f7d14a9', N'srodriguez@primefire.do', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (188, N'Willian', N'Bencosme', N'Willian Bencosme', N'Engineering Alarm & Fire Sprinkler', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'wbencosme@primefire.do', NULL, N'+1 8297653844', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6987d8c8-0423-43bb-be3e-6601476147ab', N'wbencosme@primefire.do', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (189, N'Wilnelia', N'Santos', N'Wilnelia Santos', N'HR Analyst', N'Hiuman Resource', N'Republica Dominicana', N'wsantos@primefire.us', NULL, N'+1 7877613180', N'+1 8608413625', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'be4788a5-f480-442d-ab40-209e317e54ac', N'wsantos@primefire.us', '2026-03-13 00:46:46', NULL, NULL, NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[employees] OFF
GO


-- Data for customers (5 records)
SET IDENTITY_INSERT [dbo].[customers] ON
GO

INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (3, N'commercial', N'Romo Life Safety', N'Andres', N'Romo', N'Adrian', N'engineering', N'medium', N'andy@romofiresystems.com', N'+1 972 742 0081', 3, '2026-02-23 23:49:35', '2026-02-24 00:09:58', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (4, N'commercial', N'PrimeFire', N'Alberto', NULL, N'Rodriguez', N'engineering', N'high', N'arodriguez@primefire.us', N'+ 1 787 221 2121', 4, '2026-02-23 23:52:39', '2026-02-23 23:53:16', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (5, N'commercial', N'Licensed Massage Pros', N'Virginia', N'Gonzalez', N'Gonzalez', N'commercial', N'medium', N'lnfo@licensedmassagepros.com', N'+1 682 377 6189', 5, '2026-02-23 23:57:15', '2026-02-23 23:57:25', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (6, N'commercial', N'Havana NRG', N'Mariela', N'Suarez', NULL, N'individual', N'medium', N'havananrgbookings@gmail.com', N'+1 214 597 1970', 6, '2026-02-24 00:02:52', '2026-02-24 00:09:36', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (7, N'commercial', N'Speedy Gonzalez Welding', N'Mireya', N'Gomez', NULL, N'individual', N'medium', N'speedygonzalezwelding@gmail.com', N'+1 (214) 284-1088', 7, '2026-02-24 00:09:22', NULL, 2)

SET IDENTITY_INSERT [dbo].[customers] OFF
GO


-- customer_alternate_contacts: No data to insert


-- customer_attachments: No data to insert


-- customer_notes: No data to insert


-- departments: No data to insert


-- Data for roles (5 records)
SET IDENTITY_INSERT [dbo].[roles] ON
GO

INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (1, N'Admin', N'System Administrator with full access')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (2, N'Manager', N'Department manager with elevated permissions')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (3, N'User', N'Standard user with basic access')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (5, N'Jobs ', N'Administrador modulo Jobs')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (8, N'Admin_Tenants', N'Tenants')

SET IDENTITY_INSERT [dbo].[roles] OFF
GO


-- Data for employee_roles (3 records)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 1)
GO


-- Data for tenants (1 records)
SET IDENTITY_INSERT [dbo].[tenants] ON
GO

INSERT [dbo].[tenants] ([tenant_id], [name], [db_connection_key], [description], [is_active], [created_at]) VALUES (1, N'DevRomo', N'MAIN', N'Developer''s Romo', 1, '2026-01-25 18:49:45')

SET IDENTITY_INSERT [dbo].[tenants] OFF
GO


-- external_users: No data to insert


-- Data for hardware_inventory (2 records)
SET IDENTITY_INSERT [dbo].[hardware_inventory] ON
GO

INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (2, N'AA18250', N'Dell', N'Alienware 18 Area 51 AA18250', N'Laptop', N'Intel Core TM Ultra 9 275H', NULL, N'NVMe', 1860, NULL, N'Windows 11 Pro', '2025-11-12', '2026-11-12', '2025-11-12', 2, N'Dallas ', N'Active', N'Laptop Andy Principal ', '2026-02-19 23:51:48', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (3, N'6L7KQ73', N'Dell', N'Alienware ', N'Laptop', N'Intel Core(TM) i9-10900 CPU', NULL, N'NVMe', 954, NULL, N'Windows 11 Home', '2023-01-01', '2024-01-01', '2023-01-01', 2, N'Grand Preire ', N'Active', N'Laptop de Backup', '2026-02-20 22:42:42', NULL)

SET IDENTITY_INSERT [dbo].[hardware_inventory] OFF
GO


-- holidays: No data to insert


-- jobs: No data to insert


-- Data for licenses (32 records)
SET IDENTITY_INSERT [dbo].[licenses] ON
GO

INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (1, N'Revit ', N'2025', '2025-03-10', '2026-03-10', N'Subscription', N'mmarquezia7@gmail.com', N'NA', 2, N'Licencia de Maria Angela ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (2, N'Revit ', N'2025', '2025-05-30', '2026-05-30', N'Subscription ', N'Barrioscastillosky@gmail.com', N'NA', 2, N'Licencia de Katherine Barrios')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (3, N'Revit ', N'2025', '2025-06-06', '2026-06-06', N'575-19015855', N'Rosiul.bulle@gmail.com', N'NA', 2, N'Licencia de Rosio Bulle')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (4, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'575-07753858', N'Oscar ', N'NA', 2, N'Licencia Oscar ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (5, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'574-60008874', N'Jose Gabriel Barrios', N'NA', 2, N'Licencia de Jose Gabriel Berrios')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (6, N'Revit ', N'2025', '2025-05-10', '2026-05-10', N'575-19015855', N'Ricardo Petit', N'NA', 2, N'Licencia de Ricardo Petit')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (7, N'Revit ', N'2026', '2025-09-24', '2026-09-24', N'jesusgazporua@gmail.com', N'Jesus Gonzalez', N'NA', 2, N'Licencia Jesus Gonzalez')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (8, N'Revit ', N'2025', '2025-06-10', '2026-06-10', N'575-19015855', N'Maria Jose', N'NA', 2, N'Licencia de María José: en octubre vence la de AutoCAD.')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (9, N'AutoCAD', N'2026', '2025-11-11', '2026-11-11', N'575-21731657-001R1', N'Henry Mujica', N'NA', 2, N'2 icencias AutoCAD Henry')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (10, N'AutoCAD', N'2026', '2025-11-11', '2026-11-11', N'575-21732053-001R1', N'Henry Mujica', N'NA', 2, N'Clientes Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (11, N'Revit ', N'2025', '2025-12-05', '2026-12-05', N'574-60008874', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (12, N'Revit ', N'2025', '2025-12-05', '2026-12-05', N'574-73836720', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (13, N'Revit ', N'2025', '2025-09-01', '2026-09-01', N'Subscription', N'alirio.rojas@gmail.com', N'NA', 2, N'Cuenta de Alirio')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (14, N'McFee', N'Profesional', '2025-12-01', '2026-12-01', N'Subscription', N'Victor Valencia ', N'NA', 2, N'Se instalo Bluebeam y McFee
ahi que borrar la tarjeta de Credito de McFee')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (15, N'Revit ', N'2025', '2026-01-01', '2026-05-05', N'575-07754749', N'manueledu22@gmail.com/Manuel Jimenez', N'NA', 2, N'Se asigno la Licencia 575-07754749, pero no funciono. se cambio por subscripcion hay que recordar al proveedor cada 3 meses')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (16, N'Revit ', N'2025', '2026-03-10', '2027-03-10', N'vilchezwm@gmail.com', N'Wilhired Vilchez', N'NA', 2, N'Se habia instalado La Licencia con el Serial Number: 575-46607110, pero no funciono se instalo con proveedor y hay que renovar cada 3 meses ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (17, N'AutoCAD ', N'2026', '2025-12-01', '2026-12-01', N'jony_romo@hotmail.com', N'Andy Romo', N'NA', 2, N'Licencia por subscripcion ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (18, N'Windows ', N'11 Pro', '2025-12-01', '2030-12-31', N'9X4N6-W26CD-3MK3M-6VK4R-7H66T', N'Roby Romo RLS', N'NA', 2, N'Licencia W11 Pro Roberto Romo')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (19, N'McFee', N'Antivirus Plus', '2026-05-27', '2027-05-27', N'Subscription', N'info@devromo.com', N'NA', 2, N'Antivirys McFee
Activo en computadora personal,
Roby, Aryanna, Andy')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (20, N'ZerosSSL', N'Certificado SSL', '2026-01-01', '2027-01-01', N'Subscription', N'eliasvillegazcruz@gmail.com', N'NA', 2, N'Cuenta que hay que pagar anualmente con Elias')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (25, N'Godaddy', N'Webpage RLS', '2026-01-27', '2027-01-27', N'Subscripcion', N'andy@romolifesafety.com', N'NA', 2, N'Cobro Anual Webpage: Dominio Certificado SSL, Hoting, Codigo QR ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (29, N'Godaddy ', N'Webpage SWG', '2026-02-01', '2027-02-01', N'Subscription', N'speedygonzalezwelding@gmail.com', N'NA', 2, N'Webpage: Hosting, Certificado SSL, (dominio) lo tiene en m365')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (30, N'Godaddy', N'Webpage La Masajista', '2025-06-01', '2026-06-01', N'Subscription', N'licensedmassagepros@gmail.com', N'NA', 2, N'Webpage: Dominio, Certificado SSL, QR y Hosting')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (33, N'Antivirus ', N'Trend maximum 3D', '2023-09-09', '2026-09-26', N'XRMQ-0013-9700-4517-504', N'Alejandro SEDE ', N'NA', 2, N'Licencia Antivirus Alejandro clínica SEDE ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (34, N'Godaddy', N'Webpage Havana NRNG', '2025-08-01', '2026-08-01', N'Subscription', N'havananrgbookings@gmail.com', N'NA', 2, N'Webpage: Havana NRG, Dominio, Certificado SSL, Código QR, Hosting ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (35, N'Windows ', N'11 Pro', '2026-01-28', '2039-12-31', N'RNHDG-JMWXP-RQCH6-FTRKX-V22KG', N'Info@romolifesafety.com', N'NA', 2, N'Licencia de Aryanna de RLS')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (36, N'AutoCAD ', N'2026', '2026-02-19', '2027-02-19', N'575-51419614-001R1', N'Henry Mujica', N'Na', 2, N'Licencia a Henry Mujica AutoCAD 2026 1 año, se cambio por una licencia de subscripcion')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (37, N'Revit ', N'Revit Subscription', '2026-02-20', '2027-02-20', N'ybuitragov@gmail.com', N'Henri Mujica', N'NA', 2, N'Licencia de Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (38, N'Revit ', N'2026', '2026-02-26', '2027-02-26', N'Subscription ', N'trossell5@gmail.com', N'NA', 2, N'Licencia de Henry Mujica ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (39, N'AutoCAD ', N'2025', '2026-03-02', '2027-02-22', N'575-50292219:001Q1', N'Oscar CA Services ', N'NA', 2, N'Licencia a Oscar pago la de 3 años pero solo se activo por un año el key tambien se instalo Sketchup')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (40, N'Surfshark ', N'VPN', '2026-03-16', '2026-05-16', N'Subscription Trial ', N'Jony.romo001@gmail.com', N'NA', 2, N'Subscripcion de Prueba ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (41, N'Revit ', N'2026', '2026-03-17', '2027-03-17', N'Sibscription', N'montanezcristian@gmail.com', N'NA', 2, N'Licencia de Cristian Montanez')

SET IDENTITY_INSERT [dbo].[licenses] OFF
GO


-- Data for modules (16 records)
SET IDENTITY_INSERT [dbo].[modules] ON
GO

INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard and analytics', N'dashboard', N'/dashboard', 1, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (3, N'Jobs', N'jobs', N'Job postings management', N'work', N'/jobs', 2, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (5, N'Licenses', N'licenses', N'Software licenses management', N'vpn_key', N'/licenses', 5, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (6, N'Administration', N'administration', N'System administration', N'settings', N'/config', 6, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'config/permissions/roles', 6, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (8, N'Permissions', N'permissions', N'Module permissions management', N'lock', N'/config/permissions', 9, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (10, N'Modules', N'modules', N'modules', N'Modules', N'/config/permissions/modules', 7, 1, 6, '2025-10-18 22:40:51')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (11, N'Employees', N'employees', N'Employees Module', N'People', N'/employees', 3, 1, NULL, '2025-10-19 17:31:12')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (12, N'Tickets', N'tickets', N'', N'', N'/tickets', 10, 1, NULL, '2025-10-28 02:24:35')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (13, N'Hardware Inventory', N'hardwareInventory', N'Modulo para gestionar inventario de equipos', N'settings', N'/hardware-inventory', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'', N'/time-off/calendar', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (16, N'customers', N'customers', N'customers', N'', N'customers', 0, 1, NULL, '2026-01-29 05:13:51')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (17, N'products', N'products', N'Module to handle products for proposals', N'', N'/products', 15, 1, 16, '2026-02-14 19:00:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (18, N'Timesheet', N'timesheet', N'timesheet', N'', N'/timesheet', 0, 1, NULL, '2026-02-26 03:19:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (19, N'Quotations', N'quotations', N'Module to create quotations to a existing or new customers', N'', N'/quotations', 19, 1, 16, '2026-03-07 11:32:24')

SET IDENTITY_INSERT [dbo].[modules] OFF
GO


-- Data for products (6 records)
SET IDENTITY_INSERT [dbo].[products] ON
GO

INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (11, N'Webpages & Marketing Digital', N'Package! For only $1200 to $1800, you''ll receive everything you need to establish a strong online presence for your business. Our package includes:
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
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (13, N'Single QR ', N'QR multiporpouse Marketing', N'Product', N'NA', '5.00', '49.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:26:38')
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (14, N'2 QR''s', N'Multiporpouse QR''s Marketing', N'Product', N'NA', '7.00', '69.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:29:51')
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (15, N'3 QR''s', N'Multiporpuse Marketing', N'Product', N'NA', '10.00', '99.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:30:48')
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (16, N'Landing Page', N'A single page website, also known as a one-page website, is a type of web business card that consists of only one HTML page. Unlike a traditional website, which has multiple pages and navigation menus, a single page website displays all the essential information on a single scrolling page.
- It is more user-friendly and mobile-friendly, as it eliminates the need for clicking and loading new pages
- It is more focused and concise, as it forces you to prioritize the most vital information and messages
- It is more engaging and interactive, as it can use animations, transitions, and effects to create a seamless and immersive experience for the visitors', N'Service', N'NA', '450.00', '800.00', '0.00', N'licencia', 100, 1, '2026-03-08 06:46:01')
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at]) VALUES (17, N'Business cards + Digital QR', N'A web business card, also known as a digital business card, electronic business card, or virtual business card, is the modern take on the traditional paper business card.
Instead of being printed on physical cardstock, a web business card is a webpage containing your contact information and professional details. Like a website, it can be designed and customized to reflect your personal brand.
Here is a breakdown of how web business cards work:
•
Function: Like a paper card, it displays your name, job title, company affiliation, contact details (phone, email), and potentially a website link.
•
Benefits: They offer several advantages over physical cards. They are more eco-friendly, easier to share digitally (email, text message), can be more visually engaging, and can even include interactive features like links to your social media profiles or online portfolios.', N'Service', N'NA', '250.00', '250.00', '0.00', N'licencia', 100, 1, '2026-03-08 07:44:37')

SET IDENTITY_INSERT [dbo].[products] OFF
GO


-- quotations: No data to insert


-- quotation_items: No data to insert


-- Data for role_modules (31 records)
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 3, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 5, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 6, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 7, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 8, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 10, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 11, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 12, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 13, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 14, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 15, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 16, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 17, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 18, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 19, 1, 1, 1, 1, 1, 1, 1, '2026-03-07 11:59:33')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (2, 3, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (2, 14, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (3, 12, 1, 1, 1, 1, 1, 0, 0, '2025-12-13 16:58:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 1, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 3, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 5, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 6, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 7, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 8, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 10, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 11, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 12, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 13, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 14, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (8, 15, 1, 1, 1, 1, 1, 1, 1, '2025-12-28 05:40:41')
GO


-- Data for tenant_employees (4 records)
SET IDENTITY_INSERT [dbo].[tenant_employees] ON
GO

INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (2, 1, '2026-01-25 19:15:18', N'jcarlos.villa.rivera@gmail.com', N'$2b$12$7ICyqJKa.71h6sYo5E1eQurNLUG.RC1.m9vgguIiENvSviWT6/Kr2')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (4, 1, '2026-02-12 01:48:20', N'info@devromo.com', N'$2b$12$1t46DZil2fGeybd6TQ22Z.gUiyW8dXI4tMaU8/bEGLkSQNrqpfDCe')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (5, 1, '2026-03-05 04:00:10', N'javiermendozar73@gmail.com', N'$2b$12$5BBcHMjwPW4SygLgge2Z6uY8eHthHOuigMPf7X8CQV3xGrCD1UQQ2')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (6, 1, '2026-03-12 23:51:03', N'jony.romo001@gmail.com', N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG')

SET IDENTITY_INSERT [dbo].[tenant_employees] OFF
GO


-- Data for tenant_logos (2 records)
SET IDENTITY_INSERT [dbo].[tenant_logos] ON
GO

INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email]) VALUES (1, 1, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com', N'assets/fav/devromo.webp', NULL)
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email]) VALUES (2, 1, N'Developer''s Romo Local', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', '2026-01-25 19:41:43', N'localhost:4201', N'assets/fav/devromo.webp', NULL)

SET IDENTITY_INSERT [dbo].[tenant_logos] OFF
GO


-- tickets: No data to insert


-- ticket_messages: No data to insert


-- ticket_attachments: No data to insert


-- Data for time_off_balances (4 records)
SET IDENTITY_INSERT [dbo].[time_off_balances] ON
GO

INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (1, 2, N'personal', 2026, N'0', N'0', N'2.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (2, 2, N'vacation', 2026, N'0', N'0', N'5.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (3, 1, N'vacation', 2026, N'0', N'2.00', N'9.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (4, 2, N'sick', 2026, N'0', N'0', N'1.00', N'0')

SET IDENTITY_INSERT [dbo].[time_off_balances] OFF
GO


-- Data for time_off_requests (3 records)
SET IDENTITY_INSERT [dbo].[time_off_requests] ON
GO

INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (18, 2, N'vacation', N'pending', N'full_day', N'2026-03-16', N'2026-03-16', NULL, NULL, NULL, N'1.00', N'holliday day', NULL, NULL, NULL, N'2026-03-13 00:17:12', N'2026-03-13 00:17:12')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (19, 2, N'personal', N'pending', N'full_day', N'2026-03-17', N'2026-03-17', NULL, NULL, NULL, N'1.00', N'i need to go to the doctor', NULL, NULL, NULL, N'2026-03-13 00:17:56', N'2026-03-13 00:17:56')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (20, 2, N'sick', N'pending', N'hours', N'2026-03-18', N'2026-03-18', N'15:00:00', N'23:00:00', N'8.00', N'1.00', N'I''m going to do internally', NULL, NULL, NULL, N'2026-03-13 00:18:49', N'2026-03-13 00:18:49')

SET IDENTITY_INSERT [dbo].[time_off_requests] OFF
GO


-- Data for time_sheet_location_snapshots (10 records)
SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] ON
GO

INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (1, 1, 4, N'189.159.68.227:37844', N'25.677453', N'-100.2997179', N'11.47599983215332', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 04:31:41')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (2, 1, 4, N'189.159.68.227:57206', N'25.6774467', N'-100.299719', N'11.557000160217285', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 04:59:24')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (3, 2, 4, N'201.172.174.87:62231', N'25.76914415426781', N'-100.45508858796572', N'9.315270587075704', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 11:58:16')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (4, 2, 4, N'201.162.217.161:21712', N'25.719697193041487', N'-100.53277470156657', N'11.475186144311264', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-26 21:51:05')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (5, 2, 4, N'201.162.227.161:53100', N'25.71964568523301', N'-100.53277502193406', N'14.265556591242005', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-02-27 13:01:45')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (6, 2, 4, N'201.172.174.87:60879', N'25.76917236443903', N'-100.45506374825243', N'8.891461397408264', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 00:09:43')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (7, 2, 4, N'201.162.168.172:4275', N'25.724477216666667', N'-100.53745165000001', N'5', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 13:10:57')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (8, 2, 4, N'201.162.168.172:12222', N'25.720080033597593', N'-100.52831530355449', N'9.500300647485515', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-03 17:05:45')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (9, 2, 4, N'200.68.165.218:24807', N'25.719692578624368', N'-100.53276596899278', N'10.629695559329345', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-04 19:31:45')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (10, 2, 4, N'201.172.174.87:51592', N'25.769172215123735', N'-100.45506324598706', N'11.542115847790958', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-05 01:09:33')

SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] OFF
GO


-- Data for time_sheet_punches (5 records)
SET IDENTITY_INSERT [dbo].[time_sheet_punches] ON
GO

INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (1, 1, 4, N'2026-02-26 02:31:42', N'2026-02-26 11:59:25', N'America/Monterrey', NULL, N'25.6774467', N'-100.299719', N'11.557000160217285', NULL, NULL, NULL, NULL, 706, N'approved', N'Test', 1, N'2026-02-26 05:46:14', N'2026-02-26 04:31:42', N'2026-02-26 05:46:14')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (2, 2, 4, N'2026-02-26 11:58:17', N'2026-02-26 21:51:06', N'America/Monterrey', NULL, N'25.719697193041487', N'-100.53277470156657', N'11.475186144311264', NULL, NULL, NULL, NULL, 592, N'closed', N'Current working remote ', NULL, NULL, N'2026-02-26 11:58:17', N'2026-02-26 21:51:06')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (3, 2, 4, N'2026-02-27 13:01:46', N'2026-03-03 00:09:44', N'America/Monterrey', NULL, N'25.76917236443903', N'-100.45506374825243', N'8.891461397408264', NULL, NULL, NULL, NULL, 4987, N'closed', N'Working with prime fire in the app', NULL, NULL, N'2026-02-27 13:01:46', N'2026-03-03 00:09:44')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (4, 2, 4, N'2026-03-03 13:10:57', N'2026-03-03 17:05:49', N'America/Monterrey', NULL, N'25.720080033597593', N'-100.52831530355449', N'9.500300647485515', NULL, NULL, NULL, NULL, 234, N'closed', NULL, NULL, NULL, N'2026-03-03 13:10:57', N'2026-03-03 17:05:49')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (5, 2, 4, N'2026-03-04 19:31:46', N'2026-03-05 01:09:34', N'America/Monterrey', NULL, N'25.769172215123735', N'-100.45506324598706', N'11.542115847790958', NULL, NULL, NULL, NULL, 337, N'closed', NULL, NULL, NULL, N'2026-03-04 19:31:46', N'2026-03-05 01:09:34')

SET IDENTITY_INSERT [dbo].[time_sheet_punches] OFF
GO


-- Data for time_sheet_settings (1 records)
SET IDENTITY_INSERT [dbo].[time_sheet_settings] ON
GO

INSERT [dbo].[time_sheet_settings] ([setting_id], [overtime_daily_hours], [overtime_weekly_hours], [round_to_minutes], [is_active], [created_at], [updated_at], [max_overtime_daily_hours]) VALUES (1, N'8.00', N'40.00', NULL, 1, N'2026-02-26 03:20:13', N'2026-02-26 03:20:13', N'8.00')

SET IDENTITY_INSERT [dbo].[time_sheet_settings] OFF
GO


-- =============================================
-- FOREIGN KEYS
-- =============================================

ALTER TABLE [dbo].[addresses] WITH CHECK ADD CONSTRAINT [fk_addresses_countries]
FOREIGN KEY([country_id])
REFERENCES [dbo].[countries] ([country_id])
GO
ALTER TABLE [dbo].[addresses] CHECK CONSTRAINT [fk_addresses_countries]
GO

ALTER TABLE [dbo].[customer_alternate_contacts] WITH CHECK ADD CONSTRAINT [fk_customer_alternate_contacts_customer_id_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[customer_alternate_contacts] CHECK CONSTRAINT [fk_customer_alternate_contacts_customer_id_customers]
GO

ALTER TABLE [dbo].[customer_attachments] WITH CHECK ADD CONSTRAINT [fk_customer_attachments_customer_id_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[customer_attachments] CHECK CONSTRAINT [fk_customer_attachments_customer_id_customers]
GO

ALTER TABLE [dbo].[customer_attachments] WITH CHECK ADD CONSTRAINT [fk_customer_attachments_created_by_employees]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[customer_attachments] CHECK CONSTRAINT [fk_customer_attachments_created_by_employees]
GO

ALTER TABLE [dbo].[customer_notes] WITH CHECK ADD CONSTRAINT [fk_customer_notes_customer_id_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[customer_notes] CHECK CONSTRAINT [fk_customer_notes_customer_id_customers]
GO

ALTER TABLE [dbo].[customer_notes] WITH CHECK ADD CONSTRAINT [fk_customer_notes_created_by_employees]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[customer_notes] CHECK CONSTRAINT [fk_customer_notes_created_by_employees]
GO

ALTER TABLE [dbo].[customers] WITH CHECK ADD CONSTRAINT [fk_customers_primary_address_id_addresses]
FOREIGN KEY([primary_address_id])
REFERENCES [dbo].[addresses] ([address_id])
GO
ALTER TABLE [dbo].[customers] CHECK CONSTRAINT [fk_customers_primary_address_id_addresses]
GO

ALTER TABLE [dbo].[customers] WITH CHECK ADD CONSTRAINT [fk_customers_created_by_employees]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[customers] CHECK CONSTRAINT [fk_customers_created_by_employees]
GO

ALTER TABLE [dbo].[employee_roles] WITH CHECK ADD CONSTRAINT [fk_employee_r_emplo_247d636f]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[employee_roles] CHECK CONSTRAINT [fk_employee_r_emplo_247d636f]
GO

ALTER TABLE [dbo].[employee_roles] WITH CHECK ADD CONSTRAINT [fk_employee_r_role_i_257187a8]
FOREIGN KEY([role_id])
REFERENCES [dbo].[roles] ([role_id])
GO
ALTER TABLE [dbo].[employee_roles] CHECK CONSTRAINT [fk_employee_r_role_i_257187a8]
GO

ALTER TABLE [dbo].[employees] WITH CHECK ADD CONSTRAINT [fk_employees_count_1dd065e0]
FOREIGN KEY([country_id])
REFERENCES [dbo].[countries] ([country_id])
GO
ALTER TABLE [dbo].[employees] CHECK CONSTRAINT [fk_employees_count_1dd065e0]
GO

ALTER TABLE [dbo].[employees] WITH CHECK ADD CONSTRAINT [fk_employees_manager_employee]
FOREIGN KEY([manager_employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[employees] CHECK CONSTRAINT [fk_employees_manager_employee]
GO

ALTER TABLE [dbo].[external_users] WITH CHECK ADD CONSTRAINT [fk_external_u_tenan_08012052]
FOREIGN KEY([tenant_id])
REFERENCES [dbo].[tenants] ([tenant_id])
GO
ALTER TABLE [dbo].[external_users] CHECK CONSTRAINT [fk_external_u_tenan_08012052]
GO

ALTER TABLE [dbo].[hardware_inventory] WITH CHECK ADD CONSTRAINT [fk_hardware_i_emplo_0e240dfc]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[hardware_inventory] CHECK CONSTRAINT [fk_hardware_i_emplo_0e240dfc]
GO

ALTER TABLE [dbo].[jobs] WITH CHECK ADD CONSTRAINT [fk_jobs_countries]
FOREIGN KEY([country_id])
REFERENCES [dbo].[countries] ([country_id])
GO
ALTER TABLE [dbo].[jobs] CHECK CONSTRAINT [fk_jobs_countries]
GO

ALTER TABLE [dbo].[modules] WITH CHECK ADD CONSTRAINT [fk_modules_parent_m_19ffd4fc]
FOREIGN KEY([parent_module_id])
REFERENCES [dbo].[modules] ([module_id])
GO
ALTER TABLE [dbo].[modules] CHECK CONSTRAINT [fk_modules_parent_m_19ffd4fc]
GO

ALTER TABLE [dbo].[quotation_items] WITH CHECK ADD CONSTRAINT [fk_quotation_items_product]
FOREIGN KEY([product_id])
REFERENCES [dbo].[products] ([id])
GO
ALTER TABLE [dbo].[quotation_items] CHECK CONSTRAINT [fk_quotation_items_product]
GO

ALTER TABLE [dbo].[quotation_items] WITH CHECK ADD CONSTRAINT [fk_quotation_items_quotation]
FOREIGN KEY([quotation_id])
REFERENCES [dbo].[quotations] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[quotation_items] CHECK CONSTRAINT [fk_quotation_items_quotation]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [fk_quotations_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [fk_quotations_customers]
GO

ALTER TABLE [dbo].[role_modules] WITH CHECK ADD CONSTRAINT [fk_role_modul_modul_21a0f6c4]
FOREIGN KEY([module_id])
REFERENCES [dbo].[modules] ([module_id])
GO
ALTER TABLE [dbo].[role_modules] CHECK CONSTRAINT [fk_role_modul_modul_21a0f6c4]
GO

ALTER TABLE [dbo].[role_modules] WITH CHECK ADD CONSTRAINT [fk_role_modul_role_i_20acd28b]
FOREIGN KEY([role_id])
REFERENCES [dbo].[roles] ([role_id])
GO
ALTER TABLE [dbo].[role_modules] CHECK CONSTRAINT [fk_role_modul_role_i_20acd28b]
GO

ALTER TABLE [dbo].[ticket_attachments] WITH CHECK ADD CONSTRAINT [fk_ticket_att_ticke_30e33a54]
FOREIGN KEY([ticket_message_id])
REFERENCES [dbo].[ticket_messages] ([ticket_message_id])
GO
ALTER TABLE [dbo].[ticket_attachments] CHECK CONSTRAINT [fk_ticket_att_ticke_30e33a54]
GO

ALTER TABLE [dbo].[ticket_attachments] WITH CHECK ADD CONSTRAINT [fk_ticket_att_ticke_2fef161b]
FOREIGN KEY([ticket_id])
REFERENCES [dbo].[tickets] ([ticket_id])
GO
ALTER TABLE [dbo].[ticket_attachments] CHECK CONSTRAINT [fk_ticket_att_ticke_2fef161b]
GO

ALTER TABLE [dbo].[ticket_messages] WITH CHECK ADD CONSTRAINT [fk_ticket_mes_user_i_2d12a970]
FOREIGN KEY([user_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[ticket_messages] CHECK CONSTRAINT [fk_ticket_mes_user_i_2d12a970]
GO

ALTER TABLE [dbo].[ticket_messages] WITH CHECK ADD CONSTRAINT [fk_ticket_mes_ticke_2c1e8537]
FOREIGN KEY([ticket_id])
REFERENCES [dbo].[tickets] ([ticket_id])
GO
ALTER TABLE [dbo].[ticket_messages] CHECK CONSTRAINT [fk_ticket_mes_ticke_2c1e8537]
GO

ALTER TABLE [dbo].[tickets] WITH CHECK ADD CONSTRAINT [fk_tickets_created_284df453]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[tickets] CHECK CONSTRAINT [fk_tickets_created_284df453]
GO

ALTER TABLE [dbo].[tickets] WITH CHECK ADD CONSTRAINT [fk_tickets_assigne_2942188c]
FOREIGN KEY([assigned_to])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[tickets] CHECK CONSTRAINT [fk_tickets_assigne_2942188c]
GO

ALTER TABLE [dbo].[time_off_balances] WITH CHECK ADD CONSTRAINT [fk_time_off_balances_employee]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_off_balances] CHECK CONSTRAINT [fk_time_off_balances_employee]
GO

ALTER TABLE [dbo].[time_off_requests] WITH CHECK ADD CONSTRAINT [fk_time_off_requests_employee]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_off_requests] CHECK CONSTRAINT [fk_time_off_requests_employee]
GO

ALTER TABLE [dbo].[time_off_requests] WITH CHECK ADD CONSTRAINT [fk_time_off_requests_reviewed_by]
FOREIGN KEY([reviewed_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_off_requests] CHECK CONSTRAINT [fk_time_off_requests_reviewed_by]
GO

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [fk_time_sheet_custo_32ab8735]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [fk_time_sheet_custo_32ab8735]
GO

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [fk_time_sheet_emplo_31b762fc]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [fk_time_sheet_emplo_31b762fc]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_custo_2de6d218]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_custo_2de6d218]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_emplo_2cf2addf]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_emplo_2cf2addf]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_appro_2edaf651]
FOREIGN KEY([approved_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_appro_2edaf651]
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
