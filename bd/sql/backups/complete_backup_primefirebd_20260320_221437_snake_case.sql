USE [primefirebd]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-03-20 22:14:37 ******/
/****** Database: primefirebd on server-primefiredb.database.windows.net ******/
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
    [description] [nvarchar](1000) NULL,
    [type] [varchar](20) NOT NULL,
    [sku] [nvarchar](100) NULL,
    [unit_price] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [cost] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax_rate] [decimal](5,4) NOT NULL DEFAULT ((0)),
    [unit] [nvarchar](50) NOT NULL DEFAULT ('pieza'),
    [stock_quantity] [int] NOT NULL DEFAULT ((0)),
    [is_active] [bit] NOT NULL DEFAULT ((1)),
    [created_at] [datetime2] NOT NULL DEFAULT (sysdatetime()),
 CONSTRAINT [pk_products_3214ec07d1f91339] PRIMARY KEY CLUSTERED
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
 CONSTRAINT [pk_quotatio_3214ec079f1c6400] PRIMARY KEY CLUSTERED
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
 CONSTRAINT [pk_quotatio_3214ec074ec3b0f6] PRIMARY KEY CLUSTERED
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
    [tenant_id] [int] NOT NULL,
    [employee_id] [int] NOT NULL,
    [status] [varchar](20) NOT NULL,
    [IsDefault] [bit] NOT NULL,
    [created_at] [datetime] NOT NULL,
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
    [city] [nvarchar](100) NULL,
    [region] [nvarchar](100) NULL,
    [country] [nvarchar](100) NULL,
    [timezone] [varchar](80) NULL,
    [location_raw] [nvarchar](MAX) NULL,
    [captured_at] [varchar](19) NOT NULL,
 CONSTRAINT [pk_time_sheet_location_snapshots] PRIMARY KEY CLUSTERED
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
    [city] [nvarchar](100) NULL,
    [region] [nvarchar](100) NULL,
    [country] [nvarchar](100) NULL,
    [location_raw] [nvarchar](MAX) NULL,
    [worked_minutes] [int] NOT NULL DEFAULT ((0)),
    [status] [varchar](20) NOT NULL DEFAULT ('open'),
    [Note] [nvarchar](MAX) NULL,
    [approved_by] [int] NULL,
    [approved_at] [varchar](19) NULL,
    [created_at] [varchar](19) NOT NULL,
    [updated_at] [varchar](19) NOT NULL,
 CONSTRAINT [pk_time_sheet_punches] PRIMARY KEY CLUSTERED
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
    [overtime_daily_hours] [varchar](10) NOT NULL DEFAULT ('8.00'),
    [overtime_weekly_hours] [varchar](10) NULL DEFAULT ('40.00'),
    [round_to_minutes] [int] NULL,
    [is_active] [bit] NOT NULL DEFAULT ((1)),
    [created_at] [varchar](19) NOT NULL,
    [updated_at] [varchar](19) NOT NULL,
    [max_overtime_daily_hours] [nvarchar](10) NULL,
 CONSTRAINT [pk_time_sheet_settings] PRIMARY KEY CLUSTERED
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


-- Data for addresses (1 records)
SET IDENTITY_INSERT [dbo].[addresses] ON
GO

INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (1, N'Plaza Galerias #3', NULL, N'Santo Domingo', N'RD', N'123456', 3, NULL, 0, NULL, '2026-02-19 16:30:33')

SET IDENTITY_INSERT [dbo].[addresses] OFF
GO


-- curriculums: No data to insert


-- Data for employees (49 records)
SET IDENTITY_INSERT [dbo].[employees] ON
GO

INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (1, N'Admin', N'Guaynabo', N'Admin Guaynabo', NULL, NULL, NULL, N'Administration@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'8eeb508a-9f43-41ec-80dc-36a63c0aea48', N'Administration@primefire.us', '2026-01-13 20:41:44', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (2, N'Adolfo', N'Martinez', N'Adolfo Martinez', N'Manager Alarm Designer', N'Engineering Alarms', N'Home Office TX', N'amartinez@primefire.us', NULL, N'+1 4075584334', N'+1 4075584334', N'Dallas, TX', N'Dallas', N'Texas (TX)', N'75202', 1, N'1e7152f1-aaf5-4789-9da4-e74d9b586843', N'amartinez@primefire.us', '2025-11-06 18:15:59', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (3, N'Jose Alberto', N'Rodriguez', N'Jose Alberto Rodriguez', N'President & CEO', N'President', N'Trujillo Alto, Puerto Rico', N'arodriguez@primefire.us', NULL, N'+1 7872212121', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b826abb3-30c8-4369-8d87-ce0d648e7fba', N'arodriguez@primefire.us', '2025-11-06 18:15:59', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (4, N'Baxter', N'Jayuya', N'Baxter Jayuya', N'Engineering Alarm', N'Engineering Alarm Designer', N'Guaynabo, Puerto Rico', N'bjayuya@primefire.us', NULL, NULL, N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'b9de2f69-4aba-42f3-87eb-da0e1dcf2cfa', N'bjayuya@primefire.us', '2025-11-06 18:16:00', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (5, N'Christopher', N'Carballo Rosado', N'Christopher Carballo Rosado', N'Fire Alarm Manager', N'Alarm Project Manager', N'Guaynabo, Puerto Rico', N'ccarballo@primefire.us', NULL, N'+1 7872017346', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'd63e397b-31e7-424e-a2c3-993562347b04', N'ccarballo@primefire.us', '2025-11-06 18:16:00', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (6, N'Cesar', N'Figueroa Cruzado', N'Cesar Figueroa Cruzado', N'Group Leader', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'cfigueroa@primefire.us', NULL, N'+1 9398919203 ', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', NULL, N'b5ff98b3-be60-4693-aa6e-2553b941faff', N'cfigueroa@primefire.us', '2026-03-14 22:39:27', NULL, NULL, N'Santiago Rodriguez', N'srodriguez@primefire.do', 42)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (7, N'Jose Daniel', N'Agosto Rivera', N'Jose Daniel Agosto Rivera', NULL, NULL, NULL, N'dagosto@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'a5c57db5-230b-41c2-a0e7-0747f4512d2d', N'dagosto@primefire.us', '2026-03-14 22:39:27', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do', 16)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (8, NULL, NULL, N'Dominicana', NULL, NULL, NULL, N'dominicana@primefire.do', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'405c6850-50aa-490a-91f0-b666e016f12e', N'dominicana@primefire.do', '2026-03-14 22:39:27', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (9, N'Edwin', N'De Jesus', N'Edwin De Jesus', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'edejesus@primefire.us', NULL, N'+1 7876433660', N'+1 7877613180', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1efe087c-1bd7-4e77-9ec3-5577519a9871', N'edejesus@primefire.us', '2025-11-06 18:16:01', NULL, NULL, N'Edwin De Jesus', N'edejesus@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (10, N'Emmanuel', N'Desueza', N'Enmanuel Desueza', N'Project Coordinator', N'Field Technician, Office Assistant ', N'Santo Domingo, República Dominicana', N'edesueza@primefire.do', NULL, N'+1 8095011901', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'b0241d3b-03a7-45bf-a2fa-f06a76b9317d', N'edesueza@primefire.do', '2025-11-06 18:16:02', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (11, N'Edwin', N'Guilloty', N'Edwin Guilloty', N'Project Manager', N'Operations', N'Guaynabo, Puerto Rico', N'eguilloty@primefire.us', NULL, N'+1 7876433660', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'76025b90-b5a8-4ba7-809b-0da6685492f8', N'eguilloty@primefire.us', '2025-11-06 18:16:03', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (12, N'Elizaud', N'Hernandez', N'Elizaud Hernandez', N'Administration Manager', N'Administration', N'Trujillo Alto, Puerto Rico', N'ehernandez@primefire.us', NULL, N'+1 3867483621', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'ad15e516-906b-4e3f-8e4c-373134505755', N'ehernandez@primefire.us', '2025-11-06 18:16:03', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (13, N'Emilio', N'Melendez', N'Emilio Melendez', N'Field Tech', N'Logistics / Operations', N'Prime Fire DO', N'emelendez@primefire.do', NULL, NULL, NULL, N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominiaca', N'10109', 3, N'4c12442f-758b-4921-8188-b0167d3e6281', N'emelendez@primefire.do', '2025-11-06 18:16:03', NULL, NULL, N'Enmanuel Desueza', N'edesueza@primefire.do', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (14, N'Elionetzy', N'Santiago Adames', N'Elionetzy Santiago Adames', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto', N'esadames@primefire.us', NULL, N'+1 7874729866', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b892a33-b52b-4f24-9af1-941c3eceb183', N'esadames@primefire.us', '2025-11-06 18:16:04', NULL, NULL, N'Edwin Guilloty', N'eguilloty@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (15, N'Gustavo', N'Heredia', N'Gustavo Heredia', N'Designer ', NULL, NULL, N'gheredia@primefire.do', NULL, N'+1 8492854334', NULL, N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'44d8c9a2-c02f-41c7-85e0-50c9f92ec327', N'gheredia@primefire.do', '2025-11-06 18:16:04', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (16, N'Geurys Jabbart', N'Medrano Montero', N'Geurys Medrano', N'Global Inventory Manager', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'gmedrano@primefire.do', NULL, N'+1 8295594355', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6dc58092-0b27-431c-a2b6-353e2fcf4c49', N'gmedrano@primefire.do', '2025-11-06 18:16:05', NULL, NULL, N'Enmanuel Desueza', N'edesueza@primefire.do', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (17, N'Gustavo', N'Vazquez', N'Gustavo Vazquez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvazquez@primefire.us', NULL, N'1 (787) 312-7679', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'07e0c48e-bc49-4f58-9e3b-c391b4fe12c2', N'gvazquez@primefire.us', '2025-11-06 18:16:05', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (18, N'Giovanni', N'Velez', N'Giovanni Velez', N'Fire Alarm Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'gvelez@primefire.us', NULL, N'+1 7873700568', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8b6db431-ee49-46c2-be9a-2e89a493130a', N'gvelez@primefire.us', '2025-11-06 18:16:05', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (19, NULL, NULL, N'Info', NULL, NULL, NULL, N'info@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'53172d9b-ad7e-49e4-81ce-25c1c7656a3e', N'info@primefire.us', '2026-03-14 22:39:29', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (20, N'Israel', N'Nieves', N'Israel Nieves', N'Field Tech II', N'Suppression, Special  Hazards & ITM', N'Trujillo Alto, Puerto Rico', N'inieves@primefire.us', NULL, N'+1 7872047807', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'396751cd-b9ac-40e9-8122-dffb9341f319', N'inieves@primefire.us', '2025-11-06 18:16:06', NULL, NULL, N'Edwin Guilloty', N'eguilloty@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (21, N'Jonathan', N'Romo', N'Jonathan Romo', N'Admin Systems', N'IT', N'Home Office, Mexico', N'it@primefire.us', NULL, N'+528125356287', N'+528125356287', N'Arturo B de la Garza #4613', N'Monterrey', NULL, NULL, 4, N'8c882f2c-19f8-4f17-a1e8-d5644456ea65', N'it@primefire.us', '2026-03-12 14:18:55', NULL, NULL, N'Rosa M Rivera', N'rmrivera@primefire.us', 49)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (22, N'Juan', N'Aybar', N'Juan Lehtenin', N'Fire Alarm Division', N'PrimeFire DO', N'República Dominica', N'jaybar@primefire.do', NULL, NULL, N'+1 8095011901', N'Av. Abraham Lincoln', N'Santo Domingo', N'Republica Dominicana', N'10109', 3, N'2a9640a5-897f-49c0-94f7-15a6f4d642c9', N'jaybar@primefire.do', '2025-11-06 18:16:07', NULL, NULL, N'Santiago Rodriguez', N'srodriguez@primefire.do', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (23, N'Joskayra', N'de Jesus Medina', N'Joskayra de Jesus Medina', N'Engineering Alarm Designer & Accountant', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'jdejesus@primefire.do', NULL, N'+1 809-499-5821', N'+1 8095011900', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'df97493e-56d4-45fb-8a18-25a60dead4b5', N'jdejesus@primefire.do', '2025-11-06 18:16:08', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (24, N'Javier', N'Lopez Rivera', N'Javier Lopez Rivera', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jlopez@primefire.us', NULL, N'+1 9393399185', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'e809702b-2fb2-45d3-b486-04f66b89d725', N'jlopez@primefire.us', '2025-11-06 18:16:08', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (25, N'Jose', N'Martínez', N'Jose Martínez', N'Field Tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'jmartinez@primefire.us', NULL, N'+1 787-948-3352', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'1eb06cab-eeae-425b-bd0e-562d6eb89735', N'jmartinez@primefire.us', '2025-11-06 18:16:08', NULL, NULL, N'Edwin De Jesus', N'edejesus@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (26, N'Jose', N'Morales', N'Jose Morales', N'Group Leader', N'Sprinklers Division', N'Trujillo Alto, Puerto Rico', N'jmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'd96be71d-b61f-40e5-b973-94843acf7c47', N'jmorales@primefire.us', '2025-11-06 18:16:09', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (27, N'Juan', N'Villa', N'Juan Villa', N'Systems', N'IT', N'Home Office, Mexico', N'jvilla@primefire.us', N'1231231232', N'+522282553841', N'+522282553841', N'Retorno Pantochica #3', N'Xalapa', N'Veracruz', N'91098', 4, N'0523631c-d286-4be5-9aaf-e33ac83b587c', N'jvilla@primefire.us', '2025-12-27 23:43:06', N'1231231232', NULL, N'Jonathan Romo', N'it@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (28, N'Kevin', N'Morales', N'Kevin Morales', N'Administrative Assistant', N'HR Analyst', N'Trujillo Alto, Puerto Rico', N'kmorales@primefire.us', NULL, N'+1 7876295196', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'2b7ae779-a20d-47d9-9680-ccf54568ae41', N'kmorales@primefire.us', '2025-11-06 18:16:10', NULL, NULL, N'Sigfredo Carrero', N'scarrero@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (29, N'Kristian', N'Torres', N'Kristian Torres', N'Field Tech', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ktorres@primefire.us', NULL, N'+1 4077059670', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'b02a129b-cb1f-4d22-ab12-acbbeb5291e2', N'ktorres@primefire.us', '2025-11-06 18:16:10', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (30, N'Luis', N'Burset', N'Luis Burset', N'Fire Sprinklers Designer', N'Designer', N'Home Office TX', N'lburset@primefire.us', NULL, N'+1 7874855008', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR', N'00976', 2, N'88b8d661-148d-4476-881c-d42f4d3ef96e', N'lburset@primefire.us', '2025-11-06 18:16:10', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (31, N'Luis', N'De Jesus', N'Luis De Jesus', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'ldejesus@primefire.us', NULL, N'+1 7873909755', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'8d91aafe-6b6d-4994-84d4-5108e4e7b0ca', N'ldejesus@primefire.us', '2025-11-06 18:16:11', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (32, N'Luis', N'Nieves', N'Luis Nieves', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'lnieves@primefire.us', NULL, N'+1 7873641643', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'8f082fd0-cad1-4579-8305-08b31f95befd', N'lnieves@primefire.us', '2025-11-06 18:16:11', NULL, NULL, N'Sigfredo Carrero', N'scarrero@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (33, N'Max', N'Oliveras', N'Max Oliveras', N'Project Manager', N'Field Engineering', N'Trujillo Alto', N'moliveras@primefire.us', NULL, N'+ 787 607 7402', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'41b65f97-f746-46c2-b03a-9f0dffaefb19', N'moliveras@primefire.us', '2025-11-06 18:16:12', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (34, N'Marcos', N'Quiles', N'Marcos Quiles', N'Fire Protection Designer', N'Protection Designer', N'Trujillo Alto, Puerto Rico', N'mquiles@primefire.us', NULL, N'+1 7875257965', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'0f46165b-1617-4d70-82f4-f4768b01f90c', N'mquiles@primefire.us', '2025-11-06 18:16:12', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (35, N'Nathan', N'Gonzalez', N'Nathan Gonzalez', N'Engineering Alarm Designers', N'Engineering Alarm', N'Trujillo Alto, Puerto Rico', N'ngonzalez@primefire.us', NULL, N'+1 7879819444', N'+1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'c9d2250f-2b79-403f-9c13-fe11212f4ebb', N'ngonzalez@primefire.us', '2025-11-06 18:16:13', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (36, NULL, NULL, N'Printer Guaynabo', NULL, NULL, NULL, N'Printer-Guaynabo@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'5719f4d2-8092-48f8-a53a-d6f0e28bf8ea', N'Printer-Guaynabo@primefire.us', '2026-03-14 22:39:31', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (37, N'Rayneé', N'Fúnez Heredia', N'Rayneé Fúnez Heredia', N'Account Manager', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'rfunez@primefire.us', NULL, N'+1 9392350216', N'+1 7876303000 ', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'ab01cd10-bff4-4620-b55e-0d0f1ab1d151', N'rfunez@primefire.us', '2025-11-06 18:16:13', NULL, NULL, N'Giovanni Velez', N'gvelez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (38, N'Rolando', N'Rivera', N'Rolando Rivera', N'Alarm Designer', NULL, N'Guaynabo, Puerto Rico', N'rrivera@primefire.us', NULL, N'+1 7872377217', N'+1 7876303000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR (Puerto Rico)', N'00969', 2, N'706337f9-ef71-47cb-982f-2ca206383da3', N'rrivera@primefire.us', '2025-11-06 18:16:14', NULL, NULL, N'Adolfo Martinez', N'amartinez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (39, N'Sigfredo', N'Carrero', N'Sigfredo Carrero', N'General Manager / Sprinkler Division', N'SubDirection', N'Trujillo Alto, Puerto Rico', N'scarrero@primefire.us', NULL, N'+1 7876475955', N' +1 7877613180', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'b7d6932d-8c4c-411f-ab87-1547f9c07391', N'scarrero@primefire.us', '2025-11-06 18:16:14', NULL, NULL, N'Jose Alberto Rodriguez', N'arodriguez@primefire.us', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (40, NULL, NULL, N'service', NULL, NULL, NULL, N'service@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'f1228614-b6eb-4c3e-bbae-869139b6736e', N'service@primefire.us', '2026-03-14 22:39:32', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (41, N'Stephanie', N'Martinez', N'Stephanie Martinez', N'HR Analyst', N'Hiuman Resource', N'Trujillo Alto, Puerto Rico', N'smartinez@primefire.us', NULL, N'+1 8292485211', N'+1 8095011901', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'9cfcf921-1266-468c-a7de-0ee20fd472cb', N'smartinez@primefire.us', '2025-11-06 18:16:15', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (42, N'Santiago', N'Rodriguez', N'Santiago Rodriguez', N'Operation Manager', N'Field Engineering ', N'Santo Domingo, República Dominicana', N'srodriguez@primefire.do', NULL, N'+1 7876077402', N'+1 7877613180', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'635af9c2-ca37-4e5a-bfdd-989e0f7d14a9', N'srodriguez@primefire.do', '2025-11-06 18:16:15', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (43, N'Willian', N'Bencosme', N'Willian Bencosme', N'Engineering Alarm & FireSpronkler', N'Engineering Alarm Designer', N'Santo Domingo, República Dominicana', N'wbencosme@primefire.do', NULL, N'+1 8297653844', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6987d8c8-0423-43bb-be3e-6601476147ab', N'wbencosme@primefire.do', '2025-11-06 18:16:16', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (44, N'Wilnelia', N'Santos', N'Wilnelia Santos', N'HR Analyst', N'Hiuman Resource', N'Republica Dominicana', N'wsantos@primefire.us', NULL, N'+1 7877613180', N'+1 8608413625', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'be4788a5-f480-442d-ab40-209e317e54ac', N'wsantos@primefire.us', '2025-12-22 18:25:48', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (45, N'Luis', N'Belliard', N'Luis Belliard', N'Fire Sprinklers Designer', N'Engineering Alarm & Sprinkler', N'Santo Domingo, República Dominicana', N'lbelliard@primefire.do', NULL, N'+1 8292222869', N'+1 8095011901', N'Abraham Lincoln Ave, Lincoln Plaza Suite 12', N'Santo Domingo', N'Distrito Nacional (D.N.)', N'10124', 3, N'6e029e87-b520-4def-8aed-9484162bee13', N'lbelliard@primefire.do', '2025-11-13 18:05:51', NULL, NULL, N'Geurys Medrano', N'gmedrano@primefire.do', NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (46, N'Kevin', N'Lopez', N'Kevin Lopez', NULL, NULL, NULL, N'klopez@primefire.us', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'ac51c4f9-269a-44a8-99b9-aae4220a7e4e', N'klopez@primefire.us', '2026-03-14 22:39:30', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (47, N'Juan', N'Villa', N'Juan Villa', N'External User', NULL, NULL, N'jcarlos.villa.rivera@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'$2b$12$fiPTctfjmqCHlsIKwhYdGeTCs3f8WyZIrJfgTaFHM0mLKtCjqr1BW', NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (48, N'Luis D', N'Lugo', N'Luis D Lugo', N'Field tech II', N'Fire Alarm Division', N'Guaynabo, Puerto Rico', N'llugo@primefire.us', NULL, N'+1 7879514104', N'+1 7876306000', N'PR1 Km 22.3 Bo, Rio Solar Los Santa', N'Guaynabo', N'PR', N'00969', 2, N'542a5a99-aa6a-4ce9-8435-e42f587444b6', N'llugo@primefire.us', '2026-02-26 02:49:09', NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (49, N'Rosa M', N'Rivera', N'Rosa M Rivera', N'Project Manager - Ai Strategic Efficiency', N'Administration', N'Guaynabo', N'rmrivera@primefire.us', NULL, N'(787)975-9127', N'787-630-6000', N'Highway 8860 KM 1.2', N'Trujillo Alto', N'PR (Puerto Rico)', N'00976', 2, N'aa1aafd1-f175-4595-9dc1-d018b8069d66', N'rmrivera@primefire.us', '2026-03-12 14:44:19', NULL, NULL, NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[employees] OFF
GO


-- Data for customers (1 records)
SET IDENTITY_INSERT [dbo].[customers] ON
GO

INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (1, N'residential', NULL, N'Customer', N'Demo', N'Customer Demo', NULL, NULL, N'Rel@villanueva.com', N'+1 214 2345 21 34', 1, '2026-02-19 16:30:33', NULL, 21)

SET IDENTITY_INSERT [dbo].[customers] OFF
GO


-- Data for customer_alternate_contacts (1 records)
SET IDENTITY_INSERT [dbo].[customer_alternate_contacts] ON
GO

INSERT [dbo].[customer_alternate_contacts] ([customer_alternate_contact_id], [customer_id], [name], [email], [phone], [created_at], [updated_at]) VALUES (1, 1, N'Roel Villanueva', N'roel.villanueva@demo.com', NULL, '2026-02-19 16:30:38', NULL)

SET IDENTITY_INSERT [dbo].[customer_alternate_contacts] OFF
GO


-- customer_attachments: No data to insert


-- Data for customer_notes (1 records)
SET IDENTITY_INSERT [dbo].[customer_notes] ON
GO

INSERT [dbo].[customer_notes] ([customer_note_id], [customer_id], [note_text], [created_at], [updated_at], [created_by]) VALUES (1, 1, N'Demo', '2026-02-19 16:30:34', NULL, 21)

SET IDENTITY_INSERT [dbo].[customer_notes] OFF
GO


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


-- Data for employee_roles (61 records)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (3, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (4, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (5, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (5, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (6, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (7, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (8, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (9, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (10, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (10, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (11, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (11, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (12, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (13, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (14, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (15, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (16, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (17, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (18, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (18, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (19, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (20, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (21, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (21, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (21, 8)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (22, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (23, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (24, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (25, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (26, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (27, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (27, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (27, 8)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (28, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (29, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (30, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (31, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (32, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (33, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (33, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (34, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (35, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (36, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (37, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (38, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (39, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (39, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (40, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (41, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (42, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (43, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (44, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (44, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (45, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (46, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (49, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (49, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (49, 5)
GO


-- Data for tenants (2 records)
SET IDENTITY_INSERT [dbo].[tenants] ON
GO

INSERT [dbo].[tenants] ([tenant_id], [name], [db_connection_key], [description], [is_active], [created_at]) VALUES (1, N'CLIENTE_A', N'CLIENTE_A', N'Created via user registration', 0, '2025-12-21 20:11:39')
INSERT [dbo].[tenants] ([tenant_id], [name], [db_connection_key], [description], [is_active], [created_at]) VALUES (3, N'DEVROMO', N'DEVROMO', N'Developers Romo', 1, '2026-01-12 00:00:00')

SET IDENTITY_INSERT [dbo].[tenants] OFF
GO


-- Data for external_users (2 records)
SET IDENTITY_INSERT [dbo].[external_users] ON
GO

INSERT [dbo].[external_users] ([external_user_id], [email], [password_hash], [tenant_id], [created_at]) VALUES (9, N'jcarlos.villa.rivera@gmail.com', N'$2b$12$86/wa5zSinRGMtad4BiNrO77K9zNAUPRTpQl3KtGABf6/E3LqS5hq', 3, '2026-01-14 03:02:16')
INSERT [dbo].[external_users] ([external_user_id], [email], [password_hash], [tenant_id], [created_at]) VALUES (10, N'info@devromo.com', N'$2b$12$Zq0QadTdL/6ESgImpwBxT.zKkVns1Wrqrj8W9LkKrSxYRHoEswynC', 3, '2026-01-14 13:19:21')

SET IDENTITY_INSERT [dbo].[external_users] OFF
GO


-- Data for hardware_inventory (26 records)
SET IDENTITY_INSERT [dbo].[hardware_inventory] ON
GO

INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (5, N'405QCSF568390', N'LG', N'LG PC', N'Laptop', N'Intel(R) Core(TM) Ultra 7 155H (1.4 GHz)', NULL, N'SSD', 1000, NULL, N'Windows 11 Pro', '2025-01-01', '2025-01-01', '2025-01-01', 46, N'Trujillo  Alto', N'Active', N'Computadora de Kevin Lopez', '2025-11-17 22:13:57', '2025-11-25 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (6, N'601-7E07-030B2212003338', N'MILLENIUM', N'MILLENIUM', N'Laptop', N'13th Gen Intel(R) Core(TM)  i9-13900K (3.00 GHz)', NULL, N'SSD', 4000, NULL, N'Windows 11 Pro', '2024-01-01', '2026-01-01', '2024-01-01', 45, N'Republica Dominicana', N'Active', N'es maquina de Luis Belliard', '2025-11-19 22:45:00', '2025-11-25 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (7, N'6CSMVN0', N'MS-7D07', N'MS-7D07', N'Desktop', N'Intel(R) Core(TM) i9-10850K CPU @ 3.60Ghz  ( 3.60Ghz)', NULL, N'SSD', 464, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-31', 35, N'Guaynabo PR', N'Active', N'Esta com putadora es una maquina armada ', '2025-11-25 14:37:51', '2025-11-25 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (8, N'55F9HTU', N'MS-7E06', N'MS-7E06', N'Desktop', N'Intel iCore I9-14900K(3.20 Ghz)', NULL, N'SSD', 8000, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-31', 23, N'Republica Dominicana', N'Active', N'Maquina Armada', '2025-11-26 00:21:51', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (9, N'KVBN8DJ', N'Z490 UD AC-Y1', N'Z490 UD AC-Y1', N'Desktop', N'Intel(R) Core-i7 10700K', NULL, N'SSD', 1375, NULL, N'Windows 10 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 19, N'Republica Dominicana', N'Active', N'Maquina on Hold desktop (diseño) en Republica Dominicana. Compuitadora Armada

', '2025-11-28 16:38:03', '2025-12-20 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (10, N'5CD243JJ42', N'HP', N'Pavilion Laptop 15', N'Laptop', N'12th Gen Intel(R) Core(TM) i7-1255U', NULL, N'SSD', 475, NULL, N'Windows 11 Pro', '2025-12-01', '2025-12-01', '2025-12-01', 16, N'Republica Dominicana', N'Active', N'Laptop de Geurys ', '2025-12-04 21:21:40', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (12, N'2MO4271TGM', N'HP', N'ENVY TE TE01', N'Laptop', N'Intel(R) Core(TM) i5-14400 (2.50 GHz)', NULL, N'SSD', 466, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 28, N'Trujillo Alto', N'Active', N'', '2025-12-08 15:30:11', '2025-12-22 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (13, N'PF5Z0QV1', N'Lenovo', N'Legión 5 16IAX10', N'Laptop', N'Intel(R) Core(TM) Ultra 9 275HX (2.7 GHz)', NULL, N'SSD', 951, NULL, N'Windows 11 Pro', '2025-12-12', '2026-12-14', '2025-12-14', 43, N'República Dominicana ', N'Active', N'Laptop compartida William y Joskayra', '2025-12-16 14:39:23', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (14, N'0027234201758', N'DSK', N'Corsair Vengeance', N'Desktop', N'13th Gen Intel(R) Core(TM) i9-13900K (3.00 GHz)', NULL, N'SSD', 1820, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 2, N'Orlando, Florida', N'Active', N'Maquina desktop de Adolfo', '2025-12-22 13:53:29', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (15, N'et8259-2152', N'CiberPowerPC', N'Gaming PC ', N'Desktop', N'Intel(R) Core(TM) Ultra 9 285K (3.7 GHz)', NULL, N'SSD', 1810, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-01-01', 38, N'Guaynabo', N'Active', N'Máquina de Escritorio ', '2025-12-22 14:14:36', '2025-12-22 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (16, N'7FJBYS3', N'DELL', N'Inspirion 3910', N'Laptop', N'12th Gen Intel(R) Core(TM) i5-12400 (2.50 Ghz)', NULL, N'SSD', 1140, NULL, N'Windows 11 Pro', '2025-01-01', '2025-12-31', '2025-12-01', 44, N'Guaynabo', N'Active', N'Laptop de Wilnelia', '2025-12-22 17:55:58', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (17, N'0F34MHY25013HJ', N'Micrsosoft Surface', N'7 Edition', N'Laptop', N'Snapdragon(R) X 12-core X1E80100 @ 3.40 GHz (3.42 GHz)', NULL, N'NVMe', 954, NULL, N'Windows 11 Pro', '2025-06-01', '2026-06-01', '2025-06-01', 12, N'Trujillo Alto', N'Active', N'Laptop de Elizaud', '2025-12-23 14:01:15', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (19, N'NA ', N'NA - Pending', N'NA - Pending ', N'Desktop', N'Intel(R) Core (TM) i5-8400 CPU @ 2.800Ghz ', NULL, N'HDD', 224, NULL, N'Windows 10 Pro', '2023-01-01', '2024-01-01', '2023-01-01', 12, N'Trujillo Alto', N'Active', N'Desktop de Elizaud 

Pc de Gabinete pero no viene Marca, Serial Ni Modelo', '2025-12-23 14:24:58', '2025-12-23 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (20, N'TL0PHNT', N'Micro-Star International', N'MS-7C08', N'Desktop', N'Intel(R) Core (TM) i3-8100 CPU @ 3.6 Ghz', NULL, N'SSD', 224, NULL, N'Windows 10 Pro', '2023-01-01', '2024-01-01', '2023-01-01', 11, N'Trujillo ', N'Active', N'Maquina desktop de Edwin', '2025-12-23 15:36:51', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (21, N'T5PFAG00N805214', N'Asus', N'ROG G700TF', N'Desktop', N'Intel(R) Core (TM)', NULL, N'SSD', 1860, NULL, N'Windows 11 Pro', '2025-05-13', '2026-05-13', '2025-05-13', 43, N'Republica Dominicana', N'Active', N'Desktop de Willian ', '2025-12-23 18:32:54', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (22, N'ET8226-1657', N'GamingPC', N'GamingPC', N'Desktop', N'AMD Ryzen 9 7900X 12-Core Processor (4.70 GHz)', NULL, N'SSD', 1820, NULL, N'Windows 11 Pro', '2025-02-24', '2026-02-24', '2025-02-24', 32, N'Trujillo Alto', N'Active', N'Maquina desktop Luis Nieves ', '2025-12-23 20:21:22', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (23, N'408QCUK573870', N'LG', N'PC', N'Laptop', N'Intel(R) Core(TM) Ultra 7 155H (1.4 Ghz)', NULL, N'SSD', 954, NULL, N'Windiws 11 Pro', '2023-11-12', '2024-11-12', '2023-11-12', 24, N'Guaynabo', N'Active', N'Laptop en uso', '2025-12-29 16:36:46', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (24, N'Default', N'MS-7D91', N'MS-7D91', N'Desktop', N'13Th Intel (R) Core(TM) i9-13900k (3.00 Ghz)', NULL, N'SSD', 2730, NULL, N'Windows 11 Pro', '2024-08-13', '2025-08-13', '2024-08-13', 34, N'Trujillo Alto', N'Active', N'Computadora de Marcos Quiles', '2025-12-29 17:55:40', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (25, N'DQM57J2', N'Dell', N'Optiplex 3040', N'Laptop', N'Intel(R) Core(TM) i5 6500-T CPU @ 2.50 GHz', NULL, N'SSD', 477, NULL, N'Windows 11 Pro', '2022-04-02', '2023-04-04', '2022-04-04', 29, N'Guaynabo', N'Active', N'Laptop de Kristian', '2025-12-29 18:52:27', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (26, N'PW03wJET', N'Lenovo ', N'Flex 7 14IAU7', N'Laptop', N'Intel Core I7-125U', NULL, N'SSD', 477, NULL, N'Windows 11 Pro', '2024-02-02', '2025-02-02', '2024-02-02', 8, N'República Dominicana ', N'Active', N'Laptop Alessa ', '2026-01-06 13:38:17', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (27, N'B660M-HDV', N'NA', N'B660M-HDV', N'Desktop', N'Intel ICore 3 13th 3.4 Ghz', NULL, N'SSD', 477, NULL, N'Windows 10 Pro', '2016-03-15', '2017-03-15', '2016-03-15', 39, N'Trujillo Alto', N'Active', N'Computadora Desktop de Sigfredo no aparece el Service Tag', '2026-01-09 15:10:15', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (29, N'NXJDJAA00150405F6D7600', N'Acer', N'Laptop Acer NXJK7AA002 14 pulgadas', N'Laptop', N'Intel(R) Core(TM) Ultra 5 226V (2.10 GHz)', NULL, N'SSD', 1000, NULL, N'Windows 11 Pro', '2025-01-01', '2026-01-01', '2025-01-01', 6, N'Trujillo Alto', N'Active', N'', '2026-01-12 16:45:31', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (32, N'ROT4MTSB', N'Lenovo', N'ThinkPad', N'Laptop', N'Intel core i7 150u', NULL, N'SSD', 1024, NULL, N'windows 11 pro', '2025-01-01', '2026-01-01', '2025-01-01', 25, N'Guaynabo, Puerto Rico', N'Active', N'Device name	LAPTOP-ROT4MTSB
Processor	Intel(R) Core(TM) 7 150U (1.80 GHz)
Installed RAM	16.0 GB (15.7 GB usable)
Device ID	A7D14098-20B0-4D57-AB68-3EBEEAC2302E
Product ID	00330-81498-17796-AA315
Serial number	MP2MQHB1', '2026-01-23 15:30:27', '2026-01-23 00:00:00')
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (33, N'93OOKC6', N'HP', N'HP-Envy TE01-3xxx', N'Laptop', N'12th Generation Intel (R) Core(TM) i7-1270F', NULL, N'SSD', 932, NULL, N'Windows 11 Pro', '2025-10-13', '2026-10-13', '2025-10-13', 18, N'Guaynabo', N'Active', N'Laptop de Giovanni ', '2026-01-28 17:04:31', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (34, N'405QCLH568488', N'LG', N'15Z90S-H.AAB6U1', N'Laptop', N'Intel Core Ultra 7 155h', NULL, N'NVMe', 954, NULL, N'Windows 11 Pro', '2024-04-02', '2025-04-02', '2024-04-02', 33, N'Trujillo', N'Active', N'Laptop Max Oliveras', '2026-03-02 15:29:22', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (35, N'7RV3G4', N'Dell', N'Dell 16 Plus DB16250', N'Laptop', N'Intel(R) Core(TM) Ultra 9 288V (3.30 GHz)', NULL, N'SSD', 954, NULL, N'Windows 11 Pro', '2026-03-09', '2029-03-09', '2026-03-09', 49, N'Guaynabo', N'Active', N'Laptop de Rosa Maria', '2026-03-18 19:41:55', NULL)

SET IDENTITY_INSERT [dbo].[hardware_inventory] OFF
GO


-- holidays: No data to insert


-- jobs: No data to insert


-- Data for licenses (64 records)
SET IDENTITY_INSERT [dbo].[licenses] ON
GO

INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (2, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 8, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (3, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (4, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (5, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (6, N'Office Hogar y Empresas', N'2021', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (7, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 35, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (8, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (9, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (10, N'Office Hogar y Empresas', N'2019', '2025-11-01', '2030-12-31', N'.exe', N'NA', N'NA', 2, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (11, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'YY8HR-MRN7Y-GJQ22-VTYYB-PR4D9', N'NA', N'NA', 32, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (13, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'RN964-Y9TP4-C9XB3-R7JCY-F9CMK', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (14, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'6C3H9-NF4XV-M7B9T-2FKMJ-Q69VX', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (15, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'NBRB7-DXRTG-78F3J-6DH6H-X767X', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (16, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'6YPF7-NVQTX-CFRFY-K8H8K-V22MK', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (17, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2026-11-01', N'PTNYH-C3K4Y-R2V4Y-FVK7G-KTPMK', N'NA', N'NA', 29, N'')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (18, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'JW2N2-VY84G-7B4WQ-F8TRG-TJGBK', N'NA', N'NA', 43, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (19, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'X3NXY-WQF6G-6TYHP-VGMR4-JHV39', N'NA', N'NA', 16, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (20, N'Project Professional', N'2016', '2025-01-01', '2030-12-31', N'NA', N'.exe', N'NA', 33, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (22, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (23, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'KNBXT-476VY-4MD7F-WD96T-3V66T', N'NA', N'NA', 12, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (24, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'QV29N-MB22V-W77GF-V7YWD-9D726', N'NA', N'NA', 10, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (25, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'GQ632-4NHC2-874P6-WY9F3-C3726', N'NA', N'NA', 16, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (26, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'KKNY3-6G7QC-9MV22-B8FKG-H8RC6', N'NA', N'NA', 24, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (27, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'BMHN4-RV8TH-384JX-MRBQW-F3KTT', N'NA', N'NA', 3, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (28, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'JJD6F-GN9FY-Q8GR3-T6TYQ-YBH26', N'NA', N'NA', 42, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (29, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'NDQPV-Q8C4R-6DG4R-RP7JR-369TT', N'NA', N'NA', 33, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (30, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N' 7TNMC-WG9JC-FXW9P-JTYYM-QJ3GT', N'NA', N'NA', 5, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (31, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'XKKX3-N9D4Q-F2MHB-TW9VF-PPQGT', N'NA', N'NA', 41, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (32, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WN9QH-23YXT-JFJG2-GYJBY-K766T', N'NA', N'NA', 38, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (33, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WBQHR-NYK2T-RTXF7-9XYDR-JHV26', N'NA', N'NA', 43, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (34, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (35, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'WJKK4-JNQ3C-6DXMP-MBQ68-TQ726', N'NA', N'NA', 25, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (36, N'Windows 11 Pro', N'2025', '2025-12-15', '2030-12-31', N'NWFKH-V99CG-MV63M-PGQYD-7T9TT', N'NA', N'NA', 3, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (37, N'Windows 11 Pro', N'2025', '2025-12-09', '2030-12-31', N'HM2F6-NTVVH-V4YWB-7BC2M-39MP6', N'NA', N'NA', 17, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (38, N'Windows11 Pro', N'2025', '2025-12-01', '2026-12-01', N'WTNHY-BR399-MBF4T-7HHQW-VH66T', N'NA', N'NA', 3, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (39, N'Revit', N'2025', '2025-11-30', '2026-11-30', N'575-04949370', N'NA', N'NA', 23, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (40, N'Revit', N'2025', '2025-11-30', '2026-11-29', N'575-04949370', N'NA', N'NA', 43, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (41, N'Revit', N'2025', '2025-12-17', '2026-12-16', N'574-73837017', N'NA', N'NA', 23, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (42, N'Adobe Acrobat', N'2020 Standart', '2025-12-10', '2026-12-15', N'118-1981-0736-3346-2793-4534', N'NA', N'NA', 17, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (43, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 12, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (44, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 10, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (45, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1714-6444-4243-6737-2511', N'NA', N'NA', 12, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (46, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1714-6444-4243-6737-2511', N'NA', N'NA', 3, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (47, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 25, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (48, N'Adobe Acribat Pro', N'2025', '2025-12-17', '2030-12-31', N'1118-1780-2264-9622-2021-5546', N'NA', N'NA', 25, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (49, N'AlarmCAD', N'2023', '2025-02-28', '2026-02-28', N'EGBC4-CJLTC-64K8C- FA9BX-6NXUJ-9', N'Amartinez@primefire.us', N'', 2, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (50, N'AutoSPRINK Platinum', N'2024', '2026-02-03', '2027-02-03', N'9WVCN-X5X63-3TYME-GMTYJ-NMJP4-4', N'lbusert@primefire.us', N'Na', 30, N'')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (51, N'AutoSPRINK Lite', N'2024', '2025-02-04', '2026-02-04', N'ZFHG6-JYC26-X2K9A-UWQN5-9A8VK-6', N'Lnieves@primefire.us', N'NA', 32, N'La licencia ya no se va a actualizar por que es perpetua solo se quedara sin mtto')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (52, N'AutoSPRINK Lite', N'2024', '2025-02-04', '2026-02-04', N'ZFHG6-JYC26-X2K9A-UWQN5-9A8VK-6', N'Lbilleard@primefire.us', N'NA', 45, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (53, N'AlarmCAD ', N'2023', '2024-05-31', '2025-05-31', N'7HPVU-ZS2L3-Q8YA9-ZZHC7-26PPB-2 ', N'Jmedina@primefire.us', N'NA', 23, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (54, N'AlarmCAD', N'2023', '2024-03-03', '2025-03-03', N'ARFQH-LQ9N5-JMRJB-QR5NJ-C58FT-4', N'Wbencosme@primefire.us', N'NA', 43, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (55, N'AutoCAD', N'Full Version', '2025-06-06', '2026-06-06', N'NA', N'amartinez@primefire.us', N'NA', 2, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (56, N'AutoCAD', N'Full Version', '2025-03-20', '2026-03-03', N'NA', N'lnieves@primefire.us', N'NA', 32, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (57, N'AutoCAD', N'FullVersion', '2025-06-10', '2026-06-10', N'NA', N'lburset@primefire.us', N'NA', 30, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (58, N'Office Hogar y Empresas', N'2016', '2025-11-01', '2030-12-31', N'', N'NA', N'NA', 19, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (59, N'AutoCAD', N'Full Version', '2025-06-03', '2026-06-03', N'NA', N'ngonzalwz@primefire.us', N'NA', 35, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (60, N'AutoCAD ', N'LT', '2025-11-29', '2026-11-29', N'Na', N'Sofia Rodriguez', N'NA', 3, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (67, N'AutoCAD', N'AutoCAD 2025', '2025-11-27', '2026-11-27', N'574-62827022', N'NA', N' A', 23, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (68, N'AutoCAD ', N'Full Version ', '2025-06-10', '2026-06-10', N'NA', N'Arodriguez@promefire.us', N'NA', 34, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (69, N'ZenFire', N'Subscription CRM', '2026-01-05', '2027-01-05', N'Subscription', N'ALL ', N'NA', 21, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (70, N'Godaddy Dominio PrimeFire.us', N'Dominio', '2025-10-29', '2027-10-29', N'Subscription', N'30916342', N'Alberto2016', 21, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (71, N'Godaddy eliteyachtscharter.com', N'Dominio', '2026-01-18', '2027-01-18', N'Subscription', N'PrimeFirePR', N'PFP2@25!@#', 21, N'')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (72, N'Godaddy haciendapallares.com', N'Dominio', '2026-05-01', '2029-05-01', N'Subscription ', N'PrimeFirePR', N'PFP2@25!@#', 21, NULL)
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [Password], [employee_id], [notes]) VALUES (74, N'Windows 11 ', N'Pro', '2026-03-16', '2039-12-16', N'FDHVN-XCPCG-77YDX-TTYYQ-T6PKG', N'Rmrivera@primefire.us', N'Na', 49, N'Key Rosa Maria')

SET IDENTITY_INSERT [dbo].[licenses] OFF
GO


-- Data for modules (14 records)
SET IDENTITY_INSERT [dbo].[modules] ON
GO

INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard and analytics', N'dashboard', N'/dashboard', 1, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (3, N'Jobs', N'jobs', N'Job postings management', N'work', N'/jobs', 2, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (5, N'Licenses', N'licenses', N'Software licenses management', N'vpn_key', N'/licenses', 5, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (6, N'Administration', N'administration', N'System administration', N'settings', N'/config', 6, 1, NULL, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'config/permissions/roles', 6, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (8, N'Permissions', N'permissions', N'Module permissions management', N'lock', N'/config/permissions', 9, 1, 6, '2025-10-18 19:52:14')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (10, N'Modules', N'modules', N'modules', N'Modules', N'/config/permissions/modules', 7, 1, 6, '2025-10-18 22:40:51')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (11, N'Employees', N'employees', N'Employees Module', N'People', N'/employees', 2, 1, NULL, '2025-10-19 17:31:12')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (12, N'Tickets', N'tickets', N'', N'', N'/tickets', 10, 1, NULL, '2025-10-28 02:24:35')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (13, N'Hardware Inventory', N'hardwareInventory', N'Modulo para gestionar inventario de equipos', N'settings', N'/hardware-inventory', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'', N'', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (16, N'customers', N'customers', N'customers', N'', N'customers', 0, 1, NULL, '2026-02-09 23:33:12')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (17, N'Timesheet', N'timesheet', N'timesheet', N'', N'', 0, 1, NULL, '2026-02-26 03:20:49')

SET IDENTITY_INSERT [dbo].[modules] OFF
GO


-- products: No data to insert


-- quotations: No data to insert


-- quotation_items: No data to insert


-- Data for role_modules (29 records)
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 3, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 5, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 6, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 7, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 8, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 10, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 11, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 12, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 13, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:03')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 14, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 15, 0, 0, 0, 0, 0, 0, 0, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 16, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
INSERT [dbo].[role_modules] ([role_id], [module_id], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport], [AdminActions], [OtherActions], [AssignedAt]) VALUES (1, 17, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:21:02')
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


-- tenant_employees: No data to insert


-- Data for tenant_logos (2 records)
SET IDENTITY_INSERT [dbo].[tenant_logos] ON
GO

INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url]) VALUES (1, 1, N'Cliente A', N'Cliente A', N'assets/Test-Logo.webp', N'assets/test-hero.webp', NULL, NULL, NULL, '2025-12-28 00:14:01', NULL, N'localhost:4201')
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url]) VALUES (2, 3, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com')

SET IDENTITY_INSERT [dbo].[tenant_logos] OFF
GO


-- Data for tickets (98 records)
SET IDENTITY_INSERT [dbo].[tickets] ON
GO

INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (1, N'Deploy App to Azure', N'invest how to deploy the app Python and angular to Azure', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:05:03', '2025-11-25 14:16:36')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (2, N'Anydesk Column', N'Add Anydesk Column to employees Table and show ', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:06:37', '2025-11-25 14:17:05')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (3, N'Iframe Jobs Work4 PrimeFire 2 Sites', N'Add the Frame Jobs(Vacancies) to the new webpages  ', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-20 13:08:22', '2025-11-25 14:17:15')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (4, N'Migration webpage Cpanel to Plesk ', N'we need to migrate the cpanel webp app to plesk hosting', N'TODO', N'NORMAL', NULL, 21, 27, '2025-11-20 13:12:49', '2025-11-20 13:12:49')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (5, N'Carpeta Compartida Impresora Canon', N'esta carpeta es necesaria para las impresiones ', N'CLOSED', N'NORMAL', NULL, 21, 21, '2025-11-25 14:26:24', '2025-11-25 14:26:52')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (8, N'Popup Tickets Tema Negro', N'El Popup cuando se muestra se ve en negro', N'CLOSED', N'MEDIUM', NULL, 21, 27, '2025-11-26 00:39:14', '2025-11-29 20:25:14')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (9, N'Filtros Tickets Module', N'En el modulo Tickets debe de empezar con 

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
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (10, N'Validar campos mandatorios en Jobs ', N'Validación 

•Campos mandatorios en Jobs 

•Cambiar el ejemplo de Mexico City a San Juan City.



', N'CLOSED', N'NORMAL', NULL, 21, 27, '2025-11-26 01:26:25', '2025-11-29 20:25:06')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (11, N'Validación Formulario Tickets ', N'Validación campos mandatorios 

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
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (12, N'Validation Licences ', N'Campos mandatorios 

Deshabilitar expired date hasta que se llene create at.

Debe pintarse de la siguiente manera acorde las fechas



Amarillo 3 meses antes de vencer la licencia

Naranja 2 meses antes de vencer la licencia 

Rojo 1 mes antes de vencer la licencia 



Agregar nombre de usuario licencia asignada.

', N'TODO', N'NORMAL', N'1w', 21, 21, '2025-11-26 01:41:40', '2025-12-20 18:06:55')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (16, N'Instalacion de Revit - William', N'Se requiere esta instalacion de software para modelar en 3D ', N'CLOSED', N'URGENT', N'4h', 21, 27, '2025-12-02 17:20:26', '2025-12-09 17:47:27')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (17, N'Instalacion paquete Office, Luis Belliard', N'Necesito el paquete de MS office para poder acceder a los BOM de los proyectos', N'CLOSED', N'NORMAL', N'1w', 45, 21, '2025-12-02 17:40:30', '2025-12-09 17:47:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (18, N'Instalación de REVIT- Joskayra Medina', N'La instalación de este software se require para realizar modelados en 3D, ya se instaló esta mañana por el momento todo va marchando bien.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-02 19:07:06', '2025-12-03 01:15:35')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (19, N'Instalar Software Revit', N'Se requiere la instalación del software revit para el modelado de planos en 3D.', N'CLOSED', N'NORMAL', N'1h', 43, 21, '2025-12-02 19:34:47', '2025-12-03 01:15:43')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (20, N'Licencia de AlarmCAD Reasignar', N'La licencia de AlarmCAD no me funciona, ahí que reasignarla por que aparece que ya esta en uso', N'CLOSED', N'MEDIUM', N'4h', 21, 21, '2025-12-09 17:54:45', '2025-12-09 17:57:38')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (21, N'validacion siempre  To/Do sin ser editable el ticket al momento del create ', N'validacion siempre el "Status" To/Do sin ser editable el ticket al momento del create  ', N'CLOSED', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:32:42', '2025-12-10 02:53:48')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (22, N'Poner los formatos de files que soporta', N'si el modulo de Tickets soporta 

.pdf,.word,excel tipos de imagenes, cuando se suba un documento mostrar "uploaded", al momento de enviar verificar si vuelve a cargar los documentos', N'CLOSED', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:35:31', '2025-12-10 02:47:45')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (23, N'Share Knowledge Submodulos Jobs & Tickets', N'Hacer un documento que explique el como hacer un ticket & como crear un Job ', N'TODO', N'NORMAL', N'24h', 21, 27, '2025-12-10 00:39:40', '2025-12-10 00:39:40')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (25, N'support con equipo', N'se solicito asistencia para poder trabajar los PDF que no e abren ', N'CLOSED', N'NORMAL', N'4h', 46, 21, '2025-12-11 17:41:14', '2025-12-12 13:42:02')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (26, N'CONFIGURACION NUEVA PC', N'INSTALACION DE TODOS LOS PROGRAMAS DE DISEÑO  (AUTOCAD, REVIT, BLUE BEAM, SKETCHUP) PARA NUEVA LAPTOP.', N'CLOSED', N'MEDIUM', N'4h', 43, 21, '2025-12-15 14:08:46', '2025-12-19 02:48:56')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (27, N'Mover los botones de time off a Calendar', N'primero ahi que crear un modulo que se llame administration

dentro ira 

-Calendar

-TimeSheet 



y mover las secciones dentro de la primera pagina Time Off - Calendar

', N'CLOSED', N'NORMAL', N'8h', 21, 27, '2025-12-15 23:18:56', '2025-12-27 23:12:23')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (28, N'Inventory Adolfo', N'Hacer Inventario a maquina de Adolfo', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 23:51:05', '2025-12-22 14:23:22')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (29, N'Inventory Alberto', N'Hacer Inventario a maquina de Alberto', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 16:55:26', '2025-12-15 16:55:26')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (30, N'Inventory Cesar Figueroa Cruzado', N'Hacer Inventario a maquina de Cesar Figueroa Cruzado', N'CLOSED', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-12 16:45:58')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (31, N'Inventory Christopher Carballo Rosado', N'Hacer Inventario a maquina de Christopher Carballo Rosado', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (32, N'Inventory Alessa', N'Hacer Inventario a maquina de Alessa', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2026-01-06 16:49:50')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (33, N'Inventory Edwin de Jesus', N'Hacer Inventario a maquina de Edwin de Jesus', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (34, N'Inventory Edwin Guilloty', N'Hacer Inventario a maquina de Edwin Guilloty', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 15:38:50')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (35, N'Inventory Elionetzi Santiago Adames', N'Hacer Inventario a maquina de Elionetzi Santiago Adames', N'CLOSED', N'NORMAL', N'2w', 21, 27, '2025-12-15 17:12:12', '2026-01-30 19:07:08')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (36, N'Inventory Elizaud Hdz', N'Hacer Inventario a maquina de Elizaud Hdz', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 14:11:51')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (37, N'Inventory Emilio Melendez', N'Hacer Inventario a maquina de Emilio Melendez', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:11:23')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (38, N'Inventory Enmanuel Desueza', N'Hacer Inventario a maquina de Enmanuel Desueza', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (39, N'Inventory Geurys Medrano', N'Hacer Inventario a maquina de Geurys Medrano', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:32:48')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (40, N'Inventory Giovanni Velez', N'Hacer Inventario a maquina de Giovanni Velez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2026-01-29 16:09:53')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (41, N'Inventory Gustavo Vazquez', N'Hacer Inventario a maquina de Gustavo Vazquez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2026-01-26 16:39:28')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (42, N'Inventory Israel Nieves', N'Hacer Inventario a maquina de Israel Nieves', N'CLOSED', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-30 19:07:21')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (43, N'Inventory Javier Lopez Rivera', N'Hacer Inventario a maquina de Javier Lopez Rivera', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:07:09')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (44, N'Inventory Jose Daniel Agisto Rivera', N'Hacer Inventario a maquina de Jose Daniel Agisto Rivera', N'TODO', N'NORMAL', N'2w', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:07:34')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (45, N'Inventory Jose Martinez', N'Hacer Inventario a maquina de Jose Martinez', N'CLOSED', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-23 15:24:41')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (46, N'Inventory Jose Morales', N'Hacer Inventario a maquina de Jose Morales', N'TODO', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-05 23:08:29')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (47, N'Inventory Joskayra de Jesus Medina', N'Hacer Inventario a maquina de Joskayra de Jesus Medina', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:30:30')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (48, N'Inventory Kevin Lopez', N'Hacer Inventario a maquina de Kevin Lopez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 19:34:39')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (49, N'Inventory Kevin Morales', N'Hacer Inventario a maquina de Kevin Morales', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:33:55')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (50, N'Inventory Kristian Torres', N'Hacer Inventario a maquina de Kristian Torres', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-29 19:06:37')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (51, N'Inventory Luis Belliard', N'Hacer Inventario a maquina de Luis Belliard', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:16:59')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (52, N'Inventory Luis Burset', N'Hacer Inventario a maquina de Luis Burset', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (53, N'Inventory Luis De Jesus', N'Hacer Inventario a maquina de Luis De Jesus', N'CLOSED', N'NORMAL', N'1m', 21, 27, '2025-12-15 17:12:12', '2026-01-29 20:30:43')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (54, N'Inventory Luis Nieves', N'Hacer Inventario a maquina de Luis Nieves', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-23 20:23:30')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (55, N'Inventory Marcos Quiles', N'Hacer Inventario a maquina de Marcos Quiles', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-29 19:24:45')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (56, N'Inventory Max Oliveras', N'Hacer Inventario a maquina de Max Oliveras', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (57, N'Inventory Nathan Gonzalez', N'Hacer Inventario a maquina de Nathan Gonzalez', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:34:50')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (58, N'Inventory Rolando Rivera', N'Hacer Inventario a maquina de Rolando Rivera', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 14:24:16')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (59, N'Inventory Santiago Rodriguez', N'Hacer Inventario a maquina de Santiago Rodriguez', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (60, N'Inventory Sigfredo Carrero', N'Hacer Inventario a maquina de Sigfredo Carrero', N'TODO', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-15 17:12:12')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (61, N'Inventory Willian Bnecosme', N'Hacer Inventario a maquina de Willian Bnecosme', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-20 18:03:03')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (62, N'Inventory Wilnelia Santos', N'Hacer Inventario a maquina de Wilnelia Santos', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-15 17:12:12', '2025-12-22 17:56:18')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (63, N'Onedrive', N'Sync error due to not enough space', N'CLOSED', N'NORMAL', N'1h', 2, 21, '2025-12-18 18:22:04', '2025-12-19 02:46:57')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (64, N'Reinstalación de Revit ', N'La aplicación arrojo que la licencia fue caducada por lo cual, se tuvo que reinstalar el software nuevamente.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-18 20:25:26', '2025-12-19 02:46:22')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (65, N'Botón Créate debe ser Flotante ', N'Botón créate debe ser Flotante y solo debe tener acceso el admin module ', N'TODO', N'NORMAL', N'1w', 21, 21, '2025-12-20 18:05:17', '2025-12-20 18:05:17')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (66, N'Mas grises los botones del menú en White ', N'Los títulos de los submodulos no están muy visibles cuando el tema es White ', N'CLOSED', N'MEDIUM', N'2w', 21, 27, '2025-12-20 18:22:25', '2025-12-27 23:11:54')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (67, N'Inventario Nathan Gonzalez', N'Hacer inventario Nathan Gonzalez de su PC', N'CLOSED', N'NORMAL', N'2w', 21, 21, '2025-12-20 18:27:16', '2025-12-20 18:29:46')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (68, N'Configuración remota via Anydesk', N'Configuración remota via Anydesk, para trabajar remoto los días lunes 29 y martes 30 de diciembre.', N'CLOSED', N'NORMAL', N'1h', 23, 21, '2025-12-23 17:52:34', '2025-12-23 18:33:30')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (69, N'Remover configuración de Inicio automático. ', N'Remover configuración de Inicio automático.', N'CLOSED', N'NORMAL', N'1h', 43, 21, '2025-12-23 18:36:14', '2025-12-23 23:18:44')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (70, N'Improvments Licenses ', N'Change color in expire date

disabled expired date & autopopulate expire date when is creating screen then set 1 year 

show the name of the employee', N'CLOSED', N'NORMAL', N'4h', 21, 21, '2025-12-26 22:18:30', '2025-12-26 22:18:41')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (71, N'changes in Hardware inventory', N'change color acording waranty 

autopopulate waranty 

show wmployee in list', N'CLOSED', N'NORMAL', N'4h', 21, 21, '2025-12-26 22:20:40', '2026-01-05 23:14:42')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (76, N'Instalar Office Test', N'Instalar office a Kevin ', N'CLOSED', N'MEDIUM', N'4h', 21, 21, '2025-12-30 17:19:14', '2025-12-30 17:21:18')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (77, N'Push Notifications Via Email', N'-Cuando se Cree un nuevo ticket automaticamente debe llegar un correo al asigned To

-Cuando se cree un comentario debe tomar la decicion de quien esta creando el comentario y a quien va dirigido en este caso solo existe la logica de Created By y asigned to.

-En time off - Calendar el usuario quien esta realizando el ticket debe llegar una notificacion a su manager

', N'CLOSED', N'MEDIUM', N'1w', 21, 27, '2026-01-06 00:04:29', '2026-01-08 03:05:09')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (78, N'Conexion a nueva Base de datos ', N'Voy a migrar la base de datos a sql de azure 

te dejo la conexion 

Driver={ODBC Driver 18 for SQL Server};Server=tcp:server-primefiredb.database.windows.net,1433;Database=primefirebd;Uid=PrimeFire;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;', N'CLOSED', N'NORMAL', N'1w', 21, 21, '2026-01-06 00:09:00', '2026-01-26 16:10:34')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (81, N'Acceso Servidor TA', N'Se solicito acceso servidor a TA para poder acceder mas informacion de proyectos mientrsas se completa la migracion a proyectos PFP Server

', N'CLOSED', N'NORMAL', N'1h', 46, 21, '2026-01-08 12:36:53', '2026-01-08 13:52:57')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (82, N'Data of Business ', N'Buen día Emmanuel porfavor de agregar los datos que nos pide ZenFire', N'CLOSED', N'HIGH', N'24h', 21, 10, '2026-01-15 00:16:51', '2026-01-26 16:11:14')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (83, N'ZenFire Information RD', N'Buenas tardes Emmanuel 
Si me puedes asistir con la información que nos pide ZenFire para que den de alta ', N'CLOSED', N'HIGH', N'24h', 21, 10, '2026-01-15 00:19:37', '2026-01-26 16:11:03')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (84, N'ZenFire Guaynabo Informationn', N'Información de Guaynabo para darlo de alta en la plataforma de ZenFire ', N'CLOSED', N'HIGH', N'24h', 21, 18, '2026-01-15 00:22:29', '2026-01-21 12:45:54')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (85, N'ZenFire Information TA', N'Kevin porfavor agregar la información de Trujillo Alto ', N'CLOSED', N'HIGH', N'24h', 21, 28, '2026-01-15 00:26:11', '2026-01-21 12:45:36')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (86, N'Revisar ZenFire', N'Test', N'CLOSED', N'NORMAL', N'8h', 21, 3, '2026-01-17 18:28:06', '2026-01-26 16:10:45')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (87, N'Business Proposals ', N'Dentro de este modulo, ahi que poner el submodulo de Customers 
El modulo de customers debt tener la si guide the information:

Information General,
Address 
Notes
Contact
Attachments', N'CLOSED', N'NORMAL', N'2w', 21, 27, '2026-01-21 13:42:29', '2026-02-04 15:02:32')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (88, N'Outlook no funciona ', N'agregar Primefire@outlook.com
arreglar visor de outlook', N'CLOSED', N'NORMAL', N'1h', 11, 21, '2026-01-23 13:30:47', '2026-01-23 13:54:18')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (89, N'Agregar Notas a Licences ', N'Agregar Notas a Licencias ', N'CLOSED', N'NORMAL', N'8h', 21, 27, '2026-01-26 23:56:57', '2026-01-26 23:57:06')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (90, N'Agregar Customers ', N'Agregar Customers en un nuevo modulo llamado Business Proposals, dentro de este modulo agregar Customers de ZenFire  ', N'CLOSED', N'NORMAL', N'1w', 21, 27, '2026-01-26 23:59:28', '2026-02-03 18:50:52')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (91, N'Unable to login in Office365 from the browser', N'Unable to login in Office365 from the browser', N'CLOSED', N'MEDIUM', N'1h', 2, 21, '2026-02-04 20:19:29', '2026-02-04 20:21:06')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (92, N'Time Sheet Component - Componente Data User ', N'Componente de los datos del usuario', N'CLOSED', N'NORMAL', N'8h', 21, 27, '2026-02-05 00:59:06', '2026-03-03 00:17:28')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (93, N'TimeSheet - Clocking Component', N'Agregar un servicio que obtenga la localización y agregar un screenshot de la hora.
agregarla al componente clocking descripcion: 
Customer seleccionado:
1-.El customer debe ser mandatorio para activar el timesheet
2-.Cuando se hace screenshot del clocking automáticamente debe aparecer el botón Clockout', N'CLOSED', N'NORMAL', N'48h', 21, 27, '2026-02-05 01:01:10', '2026-03-03 00:17:18')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (94, N'TimeSheet - Dashboard Component', N'Agregar el UI con el prerrellenado de los servicios, agregar los filtros el componente de la lista customers descripcion: 

El TimeSheet debe ser filtrado por mes y tener un paginador según la pantalla para cubrir todos los dias.

En automático se deben llenar los campos sin embargo esos deben ser inputs que solo con el rol admin o manager pueden estar habilitados manualmente o en su caso debe haber un botón o sección donde el usuario debe pedir permisos para habilitar esos campos.

Debe haber un servicio que comunica la vacacion, enfermedad o el día festivo en automático debe llenarse desde time-off.

Exportar Excel con los títulos y data:
Aplicar un filtro de rangos de fecha para descargar el Excel
Como extra de ser posible un campo mas puede ser notas donde explique el cliente con el que efectuo las horas laboradas día a dia

', N'CLOSED', N'HIGH', N'2w', 21, 27, '2026-02-05 01:04:03', '2026-03-08 22:21:23')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (95, N'Access to Prime Services Folder (Resolved)', N'Access Request to prime services folder ', N'CLOSED', N'NORMAL', N'1h', 45, 21, '2026-02-05 19:58:56', '2026-02-05 19:59:48')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (96, N'Filtros no funcionan', N'Outlook filtra de 1 año hacia atras en el buscador', N'CLOSED', N'NORMAL', N'1h', 8, 21, '2026-02-10 16:41:11', '2026-02-10 16:41:48')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (97, N'Arreglo de firma de Outlook', N'me salen dos diferentes firmas cuando envío un email nuevo. Si se podrá arreglar con que solo salga el que dice Engineering Alarm Designer y no el de Job Safety Analyst (es posición vieja).

Gracias', N'CLOSED', N'LOW', N'1w', 35, 21, '2026-02-10 17:29:59', '2026-02-11 00:54:54')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (98, N'Instalación del programa VeriFire Tools', N'Instalación de este programa para el uso de Santiago Rodriguez, ya que su PC asignada esta averiada.', N'CLOSED', N'URGENT', N'1h', 23, 21, '2026-02-23 17:29:52', '2026-02-24 13:51:20')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (99, N'Modificacion de Firma', N'El numero secundario de mi correo está incorrecto.', N'CLOSED', N'NORMAL', N'4h', 16, 27, '2026-02-23 17:37:29', '2026-03-08 22:21:09')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (100, N'Crear email empleado', N'Crear email al empleado:
 Luis D. Lugo
Técnico Servicio Nivel II
(787)630-6000 oficina
(787)951-4104 celular
Oficina de Guaynabo', N'CLOSED', N'HIGH', N'4h', 44, 27, '2026-02-24 16:21:00', '2026-03-06 12:30:50')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (101, N'Issue Load Menu ', N'El Menu no Carga ahi que darle refresh algunas veces ', N'CLOSED', N'NORMAL', N'8h', 21, 27, '2026-02-24 23:58:31', '2026-03-08 22:20:59')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (102, N'Boton con el tema Blanco ', N'el boton create se ve el del tema negro cuando aun cuando cambiamos a tema blanco', N'CLOSED', N'NORMAL', N'4h', 21, 27, '2026-03-03 01:16:34', '2026-03-09 02:50:03')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (103, N'installation all programs ', N'install all programs Max Machine', N'CLOSED', N'MEDIUM', N'4h', 33, 21, '2026-03-04 12:45:01', '2026-03-05 19:09:15')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (104, N'New Hire!', N'Tenemos una empleada nueva que empezara a trabajar en la oficina de Guaynabo el lunes, 9 de marzo. Su nombre es Rosa M. Rivera Rivera. Su posición es Project Manager - Ai Strategic Efficiency. Necesito le crees email y accesos necesarios - one drive, proyectos, etc. Cualquier duda o pregunta contactarme al (860)841-3625. Gracias. ', N'CLOSED', N'HIGH', N'24h', 44, 21, '2026-03-04 14:11:52', '2026-03-06 01:24:11')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (105, N'Configuracion apps computadora', N'Instalar aplicaciones y servicios', N'TODO', N'NORMAL', N'4h', 49, 21, '2026-03-09 17:27:42', '2026-03-09 17:27:42')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (106, N'Add emails to forms ', N'Agregar a Giovanni y Wilnelia al form de la webpage PR 

Agregar a Enmanuel a la webpage DO ', N'TODO', N'NORMAL', N'4h', 21, 47, '2026-03-10 19:21:14', '2026-03-10 19:21:14')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (107, N'Mejora de time sheet', N'cuando el usuario le da click en Clock in automáticamente debe aparecer reflejado en start time ', N'TODO', N'NORMAL', N'4h', 21, 27, '2026-03-12 14:53:59', '2026-03-13 00:27:25')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (108, N'Mejoras TimeOFF', N'time off: no puedes pedir permisos si no existe un manager -- validacion del manager 
time off: Halliday automatico por países y enrolar a un employee por país para mostrar sus hollidays
verificar por que no funciona servicio cuando el correo no es de un dominio empresarial', N'TODO', N'NORMAL', N'4w', 21, 21, '2026-03-13 00:28:50', '2026-03-13 00:28:50')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (109, N'Issue Correo Outlook', N'Correos borrados vuelven al bandeja de inbox', N'TODO', N'NORMAL', N'4h', 28, 21, '2026-03-17 15:49:38', '2026-03-17 15:49:38')
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at]) VALUES (110, N'Ticket para JR', N'Excel', N'TODO', N'MEDIUM', N'1h', 29, 21, '2026-03-18 16:58:58', '2026-03-18 16:58:58')

SET IDENTITY_INSERT [dbo].[tickets] OFF
GO


-- Data for ticket_messages (37 records)
SET IDENTITY_INSERT [dbo].[ticket_messages] ON
GO

INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (1, 16, 21, N'Ok Willian reviso la compra de la licencia', '2025-12-02 17:22:05', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (2, 20, 21, N'Se mando correo y se esta validando con el equipo de MepCAD', '2025-12-09 17:56:09', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (5, 23, 21, N'test', '2025-12-11 02:28:30', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (6, 27, 21, N'adjunto imagen de los improvmens', '2025-12-15 23:19:27', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (7, 63, 21, N'Se borraron algunos archivos duplicados', '2025-12-19 02:46:53', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (8, 26, 21, N'Se configuró nueva PC para Willian y Joskayra con los programas de Cinstrucciom', '2025-12-19 02:48:52', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (9, 61, 21, N'Se realizó el inventario de Computadora y de la laptop', '2025-12-20 18:02:59', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (10, 51, 21, N'Inventario a su maquina', '2025-12-20 18:16:55', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (11, 39, 21, N'Se realizó inventario a la laptop', '2025-12-20 18:32:43', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (12, 49, 21, N'Se realizó inventario e instalación de licencia', '2025-12-20 18:33:52', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (13, 28, 21, N'Inventario Realizado', '2025-12-22 14:23:19', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (14, 58, 21, N'Inventario Realizado', '2025-12-22 14:23:49', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (16, 76, 21, N'Kevin Necesito una aprovacion de parte de Elizaud', '2025-12-30 17:20:11', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (17, 76, 21, N'imagen', '2025-12-30 17:20:49', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (18, 23, 27, N'test', '2026-01-05 23:44:26', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (19, 77, 27, N'test', '2026-01-08 03:12:24', '2026-01-08 03:25:58', '2026-01-08 03:25:58')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (20, 81, 21, N'listo concedido Kevin, saludos', '2026-01-08 13:52:26', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (21, 78, 21, N'ya subi la cadena de conexio', '2026-01-10 16:22:30', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (22, 78, 21, N'foto hny', '2026-01-10 16:23:12', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (23, 83, 21, N'Atacho documento', '2026-01-15 00:20:13', '2026-01-15 00:20:23', '2026-01-15 00:20:23')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (24, 84, 21, N'Atacho documento', '2026-01-15 00:23:19', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (25, 85, 21, N'Te adjunto el documento', '2026-01-15 00:27:29', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (26, 42, 21, N'Israel tiene Tablet', '2026-01-20 13:11:17', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (27, 35, 21, N'Elionetzi tiene tablet', '2026-01-20 13:11:58', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (28, 88, 21, N'Ya quedó saludos', '2026-01-23 13:54:13', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (29, 53, 21, N'Luis usa teams desde su celular personal', '2026-01-29 20:30:33', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (30, 104, 21, N'Buen dia Wilnelia,
Perfecto voy a crear el usuario en m365 y su firma. Para el lunes continuar con la instalación de los programas.
Por otra parte va a usar una laptop nueva o una de alguien mas? Quedo atento,m saludos', '2026-03-04 14:23:51', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (31, 104, 44, N'Tengo que confirmar con Alberto, pero entiendo que se le tendra que comprar una computadora nueva.', '2026-03-04 14:26:24', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (32, 104, 44, N'Ok, para su firma el telefono de la oficina es 787-630-6000 y su celular es (787)975-9127.', '2026-03-04 14:29:09', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (33, 104, 21, N'Perfecto voy avanzando en eso, si es computadora nueva voy a tomar en cuenta que también se necesitara una licencia de Windows 11 Pro, adicional de Office crees que necesite algun otro programa especifico?', '2026-03-04 14:31:28', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (34, 104, 44, N'Saludos Jonathan, Alberto está en el proceso de hacer la compra de la computadora para la nueva empleada. Entiendo que ella necesitara una licencia para los programas de Microsoft Office, si eventualmente requiere otros programas te dejo saber. Le voy a dar accesso al Chat GPT. Tambien quería dejarte saber que tenemos a Rolando Rivera y su email es rrivera@primefire.us, así que el de Rosa M. Rivera deberia ser rmrivera@primefire.us. Quedo atenta a cualquier duda o pregunta. Gracias.', '2026-03-05 18:43:07', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (35, 104, 21, N'Ya quedo listo solo faltara la licencia de Windows 11 pro para poder ingresar a Rosa a la red de prime', '2026-03-06 01:22:03', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (36, 104, 21, N'Ya quedo listo solo faltara la licencia de Windows 11 pro para poder ingresar a Rosa a la red de prime', '2026-03-06 01:22:04', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (37, 104, 21, N'Ya quedo listo solo faltara la licencia de Windows 11 pro para poder ingresar a Rosa a la red de prime', '2026-03-06 01:22:04', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (38, 104, 21, N'Ya quedo listo solo faltara la licencia de Windows 11 pro para poder ingresar a Rosa a la red de prime', '2026-03-06 01:22:04', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (40, 102, 27, N'result', '2026-03-09 02:47:45', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (41, 107, 21, N'mostrar names no ids', '2026-03-13 00:56:20', NULL, NULL)

SET IDENTITY_INSERT [dbo].[ticket_messages] OFF
GO


-- Data for ticket_attachments (6 records)
SET IDENTITY_INSERT [dbo].[ticket_attachments] ON
GO

INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (4, 23, 5, N'angular.png', N'image/png', N'tickets/23/c298fa41042247a1b4bfaa9a53f1492a.png', '2025-12-11 02:28:31')
INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (5, 27, 6, N'VacationsImproves.png', N'image/png', N'tickets/27/0d56d010084d4dd78de4e732c3d4bccd.png', '2025-12-15 23:19:29')
INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (6, 76, 17, N'sumas.jpg', N'image/jpeg', N'tickets/76/f49e6b762cac49f5ad4548465caf0131.jpg', '2025-12-30 17:20:50')
INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (7, 77, 19, N'nfpa-logo-1.png', N'image/png', N'D:/home/uploads/tickets/77/995695a047bd4734bf9a65ceaeb25021.png', '2026-01-08 03:25:59')
INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (8, 102, 40, N'Untitled.png', N'image/png', N'/home/home/uploads/tickets/102/716543f9c6894ac7b1808cc2a547ea66.png', '2026-03-09 02:47:46')
INSERT [dbo].[ticket_attachments] ([ticket_attachment_id], [ticket_id], [ticket_message_id], [file_name], [file_type], [file_path], [created_at]) VALUES (9, 107, 41, N'Screenshot 2026-03-12 185238.png', N'image/png', N'/home/home/uploads/tickets/107/c7c0f56614184af5b11c25375ac0baf9.png', '2026-03-13 00:56:21')

SET IDENTITY_INSERT [dbo].[ticket_attachments] OFF
GO


-- Data for time_off_balances (2 records)
SET IDENTITY_INSERT [dbo].[time_off_balances] ON
GO

INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (1, 21, N'sick', 2026, N'0', N'0.50', N'0.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (2, 21, N'vacation', 2026, N'0', N'3.00', N'0.00', N'0')

SET IDENTITY_INSERT [dbo].[time_off_balances] OFF
GO


-- Data for time_off_requests (3 records)
SET IDENTITY_INSERT [dbo].[time_off_requests] ON
GO

INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (1, 21, N'sick', N'approved', N'half_day', N'2026-02-12', N'2026-02-12', NULL, NULL, NULL, N'0.50', N'I feel sick ', 21, N'2026-02-19 15:58:01', NULL, N'2026-02-12 21:01:46', N'2026-02-19 15:58:01')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (2, 21, N'vacation', N'approved', N'full_day', N'2026-02-26', N'2026-02-27', NULL, NULL, NULL, N'2.00', N'Pido este dia de vacaciones por que necesito salir ', 21, N'2026-02-19 16:12:25', NULL, N'2026-02-19 16:11:29', N'2026-02-19 16:12:25')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (3, 21, N'vacation', N'approved', N'full_day', N'2026-03-16', N'2026-03-16', NULL, NULL, NULL, N'1.00', N'That day is holliday in mexico', 49, N'2026-03-12 14:48:59', NULL, N'2026-03-12 14:45:10', N'2026-03-12 14:48:59')

SET IDENTITY_INSERT [dbo].[time_off_requests] OFF
GO


-- Data for time_sheet_location_snapshots (3 records)
SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] ON
GO

INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (1, 21, 1, N'200.68.164.16:9945', N'25.72012410070058', N'-100.52835521338724', N'10.507418291305687', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-12 14:50:55')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (2, 21, 1, N'201.172.175.223:57914', N'25.769168838556393', N'-100.45509983015337', N'12.757271574563367', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-03-13 00:22:48')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (3, 49, 1, N'173.211.173.139:64306', N'18.317721496001777', N'-66.09618346379386', N'129', NULL, NULL, NULL, N'America/New_York', NULL, N'2026-03-17 11:42:49')

SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] OFF
GO


-- Data for time_sheet_punches (2 records)
SET IDENTITY_INSERT [dbo].[time_sheet_punches] ON
GO

INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (1, 21, 1, N'2026-03-12 14:50:56', N'2026-03-13 00:22:48', N'America/Monterrey', NULL, N'25.769168838556393', N'-100.45509983015337', N'12.757271574563367', NULL, NULL, NULL, NULL, 571, N'closed', NULL, NULL, NULL, N'2026-03-12 14:50:56', N'2026-03-13 00:22:48')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [Note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (2, 49, 1, N'2026-03-17 11:42:50', N'2026-03-18 12:36:15', N'America/New_York', NULL, N'18.317721496001777', N'-66.09618346379386', N'129', NULL, NULL, NULL, NULL, 1493, N'rejected', NULL, 49, N'2026-03-18 12:36:59', N'2026-03-17 11:42:50', N'2026-03-18 12:36:59')

SET IDENTITY_INSERT [dbo].[time_sheet_punches] OFF
GO


-- Data for time_sheet_settings (1 records)
SET IDENTITY_INSERT [dbo].[time_sheet_settings] ON
GO

INSERT [dbo].[time_sheet_settings] ([setting_id], [overtime_daily_hours], [overtime_weekly_hours], [round_to_minutes], [is_active], [created_at], [updated_at], [max_overtime_daily_hours]) VALUES (1, N'8.00', N'40.00', NULL, 1, N'2026-03-05 02:52:38', N'2026-03-05 02:52:38', N'8.00')

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

ALTER TABLE [dbo].[tenant_employees] WITH CHECK ADD CONSTRAINT [fk_tenant_emp_emplo_04308f6e]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[tenant_employees] CHECK CONSTRAINT [fk_tenant_emp_emplo_04308f6e]
GO

ALTER TABLE [dbo].[tenant_employees] WITH CHECK ADD CONSTRAINT [fk_tenant_emp_tenan_033c6b35]
FOREIGN KEY([tenant_id])
REFERENCES [dbo].[tenants] ([tenant_id])
GO
ALTER TABLE [dbo].[tenant_employees] CHECK CONSTRAINT [fk_tenant_emp_tenan_033c6b35]
GO

ALTER TABLE [dbo].[tenant_logos] WITH CHECK ADD CONSTRAINT [fk_tenant_log_tenan_0db9f9a8]
FOREIGN KEY([tenant_id])
REFERENCES [dbo].[tenants] ([tenant_id])
GO
ALTER TABLE [dbo].[tenant_logos] CHECK CONSTRAINT [fk_tenant_log_tenan_0db9f9a8]
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

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [FK_TimeSheetLocationSnapshots_Customer]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [FK_TimeSheetLocationSnapshots_Customer]
GO

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [FK_TimeSheetLocationSnapshots_Employee]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [FK_TimeSheetLocationSnapshots_Employee]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [FK_TimeSheetPunches_Customer]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [FK_TimeSheetPunches_Customer]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [FK_TimeSheetPunches_Employee]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [FK_TimeSheetPunches_Employee]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [FK_TimeSheetPunches_ApprovedBy]
FOREIGN KEY([approved_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [FK_TimeSheetPunches_ApprovedBy]
GO


-- =============================================
-- BACKUP SUMMARY
-- =============================================
-- Total Tables: 32
-- Total Records: 415
-- 
-- Data per table:
--   Countries: 5 records
--   Addresses: 1 records
--   Employees: 49 records
--   Customers: 1 records
--   CustomerAlternateContacts: 1 records
--   CustomerNotes: 1 records
--   Roles: 5 records
--   EmployeeRoles: 61 records
--   Tenants: 2 records
--   ExternalUsers: 2 records
--   HardwareInventory: 26 records
--   Licenses: 64 records
--   Modules: 14 records
--   RoleModules: 29 records
--   TenantLogos: 2 records
--   Tickets: 98 records
--   ticketMessages: 37 records
--   ticketAttachments: 6 records
--   TimeOffBalances: 2 records
--   TimeOffRequests: 3 records
--   TimeSheetLocationSnapshots: 3 records
--   TimeSheetPunches: 2 records
--   TimeSheetSettings: 1 records
-- =============================================

PRINT 'Complete backup restored successfully!'
PRINT 'Total records inserted: 415'
GO
