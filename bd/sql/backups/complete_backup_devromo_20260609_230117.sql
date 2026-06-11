USE [devromo]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-06-09 23:01:17 ******/
/****** Database: devromo on A2NWPLSK14SQL-v05.shr.prod.iad2.secureserver.net ******/
/****** This script contains ALL table structures and ALL data ******/

-- =============================================
-- DROP ALL TABLES
-- =============================================

IF OBJECT_ID('dbo.warehouses', 'U') IS NOT NULL
    DROP TABLE dbo.warehouses;
GO

IF OBJECT_ID('dbo.warehouse_locations', 'U') IS NOT NULL
    DROP TABLE dbo.warehouse_locations;
GO

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

IF OBJECT_ID('dbo.ticket_recurrence_config', 'U') IS NOT NULL
    DROP TABLE dbo.ticket_recurrence_config;
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

IF OBJECT_ID('dbo.product_families', 'U') IS NOT NULL
    DROP TABLE dbo.product_families;
GO

IF OBJECT_ID('dbo.product_categories', 'U') IS NOT NULL
    DROP TABLE dbo.product_categories;
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

IF OBJECT_ID('dbo.inventory_movements', 'U') IS NOT NULL
    DROP TABLE dbo.inventory_movements;
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

IF OBJECT_ID('dbo.auth_tokens', 'U') IS NOT NULL
    DROP TABLE dbo.auth_tokens;
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
-- Table: auth_tokens
-- =============================================

CREATE TABLE [dbo].[auth_tokens](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [email] [nvarchar](255) NOT NULL,
    [token] [nvarchar](512) NOT NULL,
    [token_type] [nvarchar](50) NOT NULL,
    [expires_at] [datetime2] NOT NULL,
    [used_at] [datetime2] NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (getutcdate()),
 CONSTRAINT [PK_auth_tokens] PRIMARY KEY CLUSTERED
(
    [id] ASC
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
-- Table: inventory_movements
-- =============================================

CREATE TABLE [dbo].[inventory_movements](
    [movement_id] [int] IDENTITY(1,1) NOT NULL,
    [product_id] [int] NOT NULL,
    [warehouse_id] [int] NULL,
    [movement_type] [varchar](20) NOT NULL,
    [quantity] [decimal](18,2) NOT NULL,
    [movement_date] [date] NOT NULL DEFAULT (CONVERT([date],getdate())),
    [project] [nvarchar](150) NULL,
    [po_number] [nvarchar](100) NULL,
    [notes] [nvarchar](500) NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (getdate()),
    [reference_type] [nvarchar](50) NULL,
    [reference_id] [int] NULL,
    [created_by] [nvarchar](100) NULL,
 CONSTRAINT [PK__inventor__3213E83F647095D4] PRIMARY KEY CLUSTERED
(
    [movement_id] ASC
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
    [password] [varchar](50) NULL,
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
-- Table: product_categories
-- =============================================

CREATE TABLE [dbo].[product_categories](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [family_id] [int] NOT NULL,
    [name] [varchar](100) NOT NULL,
    [description] [varchar](MAX) NULL,
    [active] [bit] NOT NULL,
 CONSTRAINT [PK__product___3213E83FF2ABC95E] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: product_families
-- =============================================

CREATE TABLE [dbo].[product_families](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [name] [varchar](100) NOT NULL,
    [description] [varchar](MAX) NULL,
    [active] [bit] NOT NULL,
    [created_at] [datetime] NOT NULL,
 CONSTRAINT [PK__product___3213E83FCC976F1E] PRIMARY KEY CLUSTERED
(
    [id] ASC
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
    [code] [nvarchar](100) NULL,
    [family] [nvarchar](100) NULL,
    [category] [nvarchar](100) NULL,
    [size] [nvarchar](100) NULL,
    [material_type] [nvarchar](100) NULL,
    [min_stock] [decimal](18,2) NULL,
    [needed_quantity] [decimal](18,2) NULL,
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
    [can_view] [bit] NOT NULL,
    [can_create] [bit] NOT NULL,
    [can_edit] [bit] NOT NULL,
    [can_delete] [bit] NOT NULL,
    [can_export] [bit] NOT NULL,
    [admin_actions] [bit] NOT NULL,
    [other_actions] [bit] NOT NULL,
    [assigned_at] [datetime] NULL,
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
-- Table: ticket_recurrence_config
-- =============================================

CREATE TABLE [dbo].[ticket_recurrence_config](
    [config_id] [int] IDENTITY(1,1) NOT NULL,
    [ticket_id] [int] NULL,
    [recurrence_type] [nvarchar](20) NOT NULL DEFAULT ('none'),
    [next_occurrence] [datetime2] NULL,
    [parent_ticket_id] [int] NULL,
    [is_active] [bit] NOT NULL DEFAULT ((1)),
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK__ticket_r__4AD1BFF18D7968F5] PRIMARY KEY CLUSTERED
(
    [config_id] ASC
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
    [created_at] [datetime2] NOT NULL,
    [updated_at] [datetime2] NOT NULL,
    [ticket_type] [nvarchar](20) NOT NULL DEFAULT ('request'),
    [in_progress_at] [datetime2] NULL,
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
    [note] [varchar](2000) NULL,
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
-- Table: warehouse_locations
-- =============================================

CREATE TABLE [dbo].[warehouse_locations](
    [warehouse_location_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [varchar](200) NOT NULL,
    [is_active] [bit] NOT NULL,
 CONSTRAINT [PK__warehous__292B0D6F65265016] PRIMARY KEY CLUSTERED
(
    [warehouse_location_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: warehouses
-- =============================================

CREATE TABLE [dbo].[warehouses](
    [warehouse_id] [int] IDENTITY(1,1) NOT NULL,
    [name] [nvarchar](100) NOT NULL,
    [location] [nvarchar](200) NULL,
    [is_active] [bit] NOT NULL DEFAULT ((1)),
    [location_id] [int] NULL,
 CONSTRAINT [PK__warehous__3213E83FF43657C5] PRIMARY KEY CLUSTERED
(
    [warehouse_id] ASC
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

INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (1, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, N'2026-02-01 02:00:09.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (2, N'Highway 8860 Km 1.2. Camino Matienzo Cintrón', NULL, N'Trujillo Alto,', N'Puerto Rico', N'00977', 1, NULL, 0, NULL, N'2026-02-06 00:14:22.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (3, N'Grand Preire', N'3423', N'West Illions', N'Texas', N'75211', 1, NULL, 0, NULL, N'2026-02-23 23:49:35.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (4, N'Highway 8860 Km 1.2', NULL, N'Trujillo Alto', N'PR', N'00977', 2, NULL, 0, NULL, N'2026-02-23 23:52:39.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (5, N'10670 N Central Expy', NULL, N'Dallas', N'Texas', N'75231', 1, NULL, 0, NULL, N'2026-02-23 23:57:15.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (6, N'N Henderson ave suite #308', NULL, N'Dallas', N'75206', N'75206', 1, NULL, 0, NULL, N'2026-02-24 00:02:52.0000000')
INSERT [dbo].[addresses] ([address_id], [address_1], [address_2], [city], [state], [zip_code], [country_id], [google_place_id], [is_validated], [validated_at], [created_at]) VALUES (7, N'Office', NULL, N'Dallas', N'TX', N'75224', 1, NULL, 0, NULL, N'2026-02-24 00:09:21.0000000')

SET IDENTITY_INSERT [dbo].[addresses] OFF
GO


-- Data for auth_tokens (18 records)
SET IDENTITY_INSERT [dbo].[auth_tokens] ON
GO

INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (1, N'jcarlos.villa.rivera@gmail.com', N'BUAHiQu8CEJeENgm-3jR6TSPrQkMnsbdxes-XupGIuo', N'magic_link', N'2026-03-27 05:07:50.694464', N'2026-03-27 04:54:01.426307', N'2026-03-27 04:52:50.694753')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (2, N'jcarlos.villa.rivera@gmail.com', N'4-od8o4hTGOmM6mxJBdVwpDJf7E-pCNB127vuwuBy0o', N'password_recovery', N'2026-03-27 05:09:36.926326', N'2026-03-31 01:27:05.458419', N'2026-03-27 04:54:36.926610')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (3, N'jcarlos.villa.rivera@gmail.com', N'JDpfO-lP5glON_yDn5CX749wRtE-j3fOp9ymqAENWYM', N'magic_link', N'2026-03-27 05:36:44.405015', N'2026-03-27 05:21:56.655894', N'2026-03-27 05:21:44.405315')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (4, N'jcarlos.villa.rivera@gmail.com', N'_zfZIvwX86Za4ncIKSJWk6yD3zpv5trTujIu1sTJXfU', N'magic_link', N'2026-03-27 05:39:45.711688', N'2026-03-27 05:24:55.138956', N'2026-03-27 05:24:45.711963')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (5, N'jcarlos.villa.rivera@gmail.com', N'-JkgMHOmYyFy8R0F7DqXBEhGy3c2MiMhlwQLGG66p5Y', N'magic_link', N'2026-03-27 05:43:09.812186', N'2026-03-27 05:28:28.316507', N'2026-03-27 05:28:09.812420')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (6, N'jcarlos.villa.rivera@gmail.com', N'w21AbngtuR2oygKZttJRxvvgNnFqWZzOK6T85wuJkO8', N'magic_link', N'2026-03-27 05:45:35.503477', N'2026-03-27 05:30:43.390196', N'2026-03-27 05:30:35.503731')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (7, N'jony.romo001@gmail.com', N'VOARFsUJqwpfGRHoRgw5Ib8R9Qr6U7zflkn2uF4xxJE', N'magic_link', N'2026-03-30 12:03:11.890063', N'2026-03-30 11:48:47.509906', N'2026-03-30 11:48:11.907630')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (8, N'info@devromo.com', N'gr5MceJ3X6XMTQdVn0lZdNrQIikWFA2M2gZanasDMmE', N'password_recovery', N'2026-03-30 12:04:43.923068', N'2026-03-30 23:43:24.845272', N'2026-03-30 11:49:43.923339')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (9, N'info@devromo.com', N'xBW4PGfuJEdNuOOD63YsfDURa6S-laZGxzg5kWY9oZY', N'password_recovery', N'2026-03-30 23:58:24.959899', N'2026-03-30 23:50:14.971956', N'2026-03-30 23:43:24.982308')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (10, N'info@devromo.com', N'wQDyjMK4XikqTwt5A59EzP4VgkO-R3eBhSLzLvYVvvU', N'password_recovery', N'2026-03-31 00:05:15.040155', N'2026-04-01 23:54:42.617754', N'2026-03-30 23:50:15.040472')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (11, N'jcarlos.villa.rivera@gmail.com', N'zxoKciFfaO8sSm76lSPXh7JTnZb3eA-At9BPzo8450I', N'magic_link', N'2026-03-31 01:07:11.757201', N'2026-03-31 00:52:26.540575', N'2026-03-31 00:52:11.757496')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (12, N'jcarlos.villa.rivera@gmail.com', N'yDT8N-4INgjxUQ0pg6Lz6Tp6_xW4pC62d3GnEasWoGc', N'magic_link', N'2026-03-31 01:41:39.819424', N'2026-03-31 01:26:50.498186', N'2026-03-31 01:26:39.819701')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (13, N'jcarlos.villa.rivera@gmail.com', N'adTjrjnoaF2Adz6eVydWVIWR6t4ymcr05e_SixShddw', N'password_recovery', N'2026-03-31 01:42:05.526217', N'2026-03-31 01:27:37.110815', N'2026-03-31 01:27:05.526517')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (14, N'info@devromo.com', N'lrJ4UG_RvID56cYy7bRjRUIZA04SzIL6Ny43YINi0rY', N'magic_link', N'2026-04-01 23:58:52.109770', N'2026-04-01 23:49:38.946689', N'2026-04-01 23:43:52.110220')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (15, N'info@devromo.com', N'Y9v0l3TPj_YdZZ-c3HCkd6j7Yawruj7aY-FtTAjycnc', N'password_recovery', N'2026-04-02 00:09:42.675176', N'2026-04-01 23:56:15.945045', N'2026-04-01 23:54:42.675454')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (16, N'jcarlos.villa.rivera@gmail.com', N'EWGPuS_uOqAzcHXHa2KXg4BFY-tdk7azbsoXyjd4eMw', N'password_recovery', N'2026-04-02 03:25:28.820210', N'2026-04-02 03:10:58.324685', N'2026-04-02 03:10:28.828442')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (17, N'jcarlos.villa.rivera@gmail.com', N'adpRU6qmComfabovLgujI-rxJm1MokJRfMTpPPOOzes', N'magic_link', N'2026-04-08 23:33:31.618788', N'2026-04-08 23:18:44.613305', N'2026-04-08 23:18:31.690025')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (18, N'jcarlos.villa.rivera@gmail.com', N'1pRN1fE8NdVhbVQJwvQ7mEJxSE3FFuMnElqlBjGkhZs', N'password_recovery', N'2026-06-02 02:10:58.790000', N'2026-06-02 01:56:31.009254', N'2026-06-02 01:55:58.790000')

SET IDENTITY_INSERT [dbo].[auth_tokens] OFF
GO


-- curriculums: No data to insert


-- Data for employees (4 records)
SET IDENTITY_INSERT [dbo].[employees] ON
GO

INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (1, N'Juan', N'Carlos', N'Juan Carlos', N'Developer', N'IT', N'MX', N'jcarlos.villa.rivera@gmail.com', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'292367b5-7d70-4d13-81cb-ee6f7c650275', NULL, NULL, NULL, N'$2b$12$86/wa5zSinRGMtad4BiNrO77K9zNAUPRTpQl3KtGABf6/E3LqS5hq', NULL, NULL, NULL)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (2, N'Jonathan', N'Romo', N'Jonathan Romo', N'External User', N'IT', N'MTY', N'info@devromo.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'08a89d51-b7c7-404a-9d2b-ee9f7440d63c', NULL, NULL, NULL, N'$2b$12$Zq0QadTdL/6ESgImpwBxT.zKkVns1Wrqrj8W9LkKrSxYRHoEswynC', N'jony.romo001', N'jony_romo@hotmail.com', 142)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (142, N'Eli', N'Romo', N'jony.romo001', N'External User', NULL, NULL, N'jony_romo@hotmail.com', NULL, N'8117445079', NULL, N'Sabater 106', N'Monterrey', N'N.L.', N'66024', NULL, N'7dffa13b-fe6f-4406-b429-93694b40284e', NULL, NULL, NULL, N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG', N'Jonathan Romo', N'info@devromo.com', 2)
INSERT [dbo].[employees] ([employee_id], [first_name], [last_name], [display_name], [title], [department], [office], [email], [phone], [mobile_phone], [office_phone], [street_address], [city], [state], [postal_code], [country_id], [azure_oid], [azure_upn], [last_synced_at], [anydesk], [password_hash], [manager], [manager_email], [manager_employee_id]) VALUES (200, N'Mario', N'Ordaz', N'Mario Ordaz', N'FullStack & M365 Jr.', N'IT', N'MTY', N'mordaz@devromo.com', NULL, N'8184636533', NULL, N'Monterrey', N'N.L', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, N'Jonathan Romo', N'info@devromo.com', NULL)

SET IDENTITY_INSERT [dbo].[employees] OFF
GO


-- Data for customers (5 records)
SET IDENTITY_INSERT [dbo].[customers] ON
GO

INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (3, N'commercial', N'Romo Life Safety', N'Andres', N'Romo', N'Adrian', N'engineering', N'medium', N'andy@romofiresystems.com', N'+1 972 742 0081', 3, N'2026-02-23 23:49:35.0000000', N'2026-02-24 00:09:58.0000000', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (4, N'commercial', N'PrimeFire', N'Alberto', NULL, N'Rodriguez', N'engineering', N'high', N'arodriguez@primefire.us', N'+ 1 787 221 2121', 4, N'2026-02-23 23:52:39.0000000', N'2026-02-23 23:53:16.0000000', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (5, N'commercial', N'Licensed Massage Pros', N'Virginia', N'Gonzalez', N'Gonzalez', N'commercial', N'medium', N'lnfo@licensedmassagepros.com', N'+1 682 377 6189', 5, N'2026-02-23 23:57:15.0000000', N'2026-02-23 23:57:25.0000000', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (6, N'commercial', N'Havana NRG', N'Mariela', N'Suarez', NULL, N'individual', N'medium', N'havananrgbookings@gmail.com', N'+1 214 597 1970', 6, N'2026-02-24 00:02:52.0000000', N'2026-02-24 00:09:36.0000000', 2)
INSERT [dbo].[customers] ([customer_id], [customer_type], [company_name], [first_name], [last_name], [additional_name], [market], [dtd_potential], [primary_email], [primary_phone], [primary_address_id], [created_at], [updated_at], [created_by]) VALUES (7, N'commercial', N'Speedy Gonzalez Welding', N'Mireya', N'Gomez', NULL, N'individual', N'medium', N'speedygonzalezwelding@gmail.com', N'+1 (214) 284-1088', 7, N'2026-02-24 00:09:22.0000000', NULL, 2)

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


-- Data for employee_roles (4 records)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (200, 1)
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

INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (3, N'6L7KQ73', N'Dell', N'Alienware ', N'Laptop', N'Intel Core(TM) i9-10900 CPU', NULL, N'NVMe', 954, NULL, N'Windows 11 Home', N'2023-01-01', N'2024-01-01', N'2023-01-01', 2, N'Grand Preire ', N'Active', N'Laptop de Backup', '2026-02-20 22:42:42', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (4, N'C9PN75X46D', N'Apple', N'MYWG3E/A', N'Other', N'A18 PRO', 20, N'SSD', 256, N'Apple 5 Nucleos', N'iOS', N'2025-03-14', N'2026-03-14', N'2025-03-14', 2, N'MTY', N'Active', N'Iphone Jonathan', '2026-04-03 06:48:18', NULL)

SET IDENTITY_INSERT [dbo].[hardware_inventory] OFF
GO


-- holidays: No data to insert


-- Data for products (6 records)
SET IDENTITY_INSERT [dbo].[products] ON
GO

INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (11, N'Webpages & Marketing Digital', N'Package! For only $1200 to $1800, you''ll receive everything you need to establish a strong online presence for your business. Our package includes:
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
Analytics to track your website''s performance.', N'Service', N'NA', '1200.00', '1800.00', '16.00', N'licencia', 100, 1, N'2026-02-25 01:23:14.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (13, N'Single QR ', N'QR multiporpouse Marketing', N'Product', N'NA', '5.00', '49.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:26:38.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (14, N'2 QR''s', N'Multiporpouse QR''s Marketing', N'Product', N'NA', '7.00', '69.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:29:51.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (15, N'3 QR''s', N'Multiporpuse Marketing', N'Product', N'NA', '10.00', '99.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:30:48.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (16, N'Landing Page', N'A single page website, also known as a one-page website, is a type of web business card that consists of only one HTML page. Unlike a traditional website, which has multiple pages and navigation menus, a single page website displays all the essential information on a single scrolling page.
- It is more user-friendly and mobile-friendly, as it eliminates the need for clicking and loading new pages
- It is more focused and concise, as it forces you to prioritize the most vital information and messages
- It is more engaging and interactive, as it can use animations, transitions, and effects to create a seamless and immersive experience for the visitors', N'Service', N'NA', '450.00', '800.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:46:01.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity]) VALUES (17, N'Business cards + Digital QR', N'A web business card, also known as a digital business card, electronic business card, or virtual business card, is the modern take on the traditional paper business card.
Instead of being printed on physical cardstock, a web business card is a webpage containing your contact information and professional details. Like a website, it can be designed and customized to reflect your personal brand.
Here is a breakdown of how web business cards work:
•
Function: Like a paper card, it displays your name, job title, company affiliation, contact details (phone, email), and potentially a website link.
•
Benefits: They offer several advantages over physical cards. They are more eco-friendly, easier to share digitally (email, text message), can be more visually engaging, and can even include interactive features like links to your social media profiles or online portfolios.', N'Service', N'NA', '250.00', '250.00', '16.00', N'licencia', 100, 1, N'2026-03-08 07:44:37.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[products] OFF
GO


-- warehouse_locations: No data to insert


-- Data for warehouses (1 records)
SET IDENTITY_INSERT [dbo].[warehouses] ON
GO

INSERT [dbo].[warehouses] ([warehouse_id], [name], [location], [is_active], [location_id]) VALUES (1, N'Main Warehouse', NULL, 1, NULL)

SET IDENTITY_INSERT [dbo].[warehouses] OFF
GO


-- Data for inventory_movements (2 records)
SET IDENTITY_INSERT [dbo].[inventory_movements] ON
GO

INSERT [dbo].[inventory_movements] ([movement_id], [product_id], [warehouse_id], [movement_type], [quantity], [movement_date], [project], [po_number], [notes], [created_at], [reference_type], [reference_id], [created_by]) VALUES (1, 16, 1, N'IN', '33.00', N'2026-06-01', N'test', N'12312', N'test', N'2026-06-01 20:10:17.4966667', N'PURCHASE', NULL, NULL)
INSERT [dbo].[inventory_movements] ([movement_id], [product_id], [warehouse_id], [movement_type], [quantity], [movement_date], [project], [po_number], [notes], [created_at], [reference_type], [reference_id], [created_by]) VALUES (2, 16, 1, N'IN', '2.00', N'2026-06-01', NULL, N'asdg', N'asdgasdg', N'2026-06-01 20:11:22.0900000', NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[inventory_movements] OFF
GO


-- jobs: No data to insert


-- Data for licenses (34 records)
SET IDENTITY_INSERT [dbo].[licenses] ON
GO

INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (1, N'Revit ', N'2025', N'2025-03-10', N'2026-03-10', N'Subscription', N'mmarquezia7@gmail.com', N'NA', 2, N'Licencia de Maria Angela ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (2, N'Revit ', N'2025', N'2026-03-10', N'2027-03-10', N'Subscription ', N'Barrioscastillosky@gmail.com', N'NA', 2, N'Licencia de Katherine Barrios 
AnyDesk 1 513 263 805')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (3, N'Revit ', N'2025', N'2025-06-06', N'2026-06-06', N'575-19015855', N'Rosiul.bulle@gmail.com', N'NA', 2, N'Licencia de Rosio Bulle')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (4, N'Revit ', N'2025', N'2025-06-10', N'2026-06-10', N'575-07753858', N'Oscar ', N'NA', 2, N'Licencia Oscar ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (5, N'Revit ', N'2025', N'2025-06-10', N'2026-06-10', N'574-60008874', N'Jose Gabriel Barrios', N'NA', 2, N'Licencia de Jose Gabriel Berrios')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (6, N'Revit ', N'2025', N'2025-05-10', N'2026-05-10', N'575-19015855', N'Ricardo Petit', N'NA', 2, N'Licencia de Ricardo Petit')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (7, N'Revit ', N'2026', N'2025-09-24', N'2026-09-24', N'jesusgazporua@gmail.com', N'Jesus Gonzalez', N'NA', 2, N'Licencia Jesus Gonzalez')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (8, N'Revit ', N'2025', N'2025-06-10', N'2026-06-10', N'575-19015855', N'Maria Jose', N'NA', 2, N'Licencia de María José: en octubre vence la de AutoCAD.')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (9, N'AutoCAD', N'2026', N'2025-11-11', N'2026-11-11', N'575-21731657-001R1', N'Henry Mujica', N'NA', 2, N'2 icencias AutoCAD Henry')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (10, N'AutoCAD', N'2026', N'2025-11-11', N'2026-11-11', N'575-21732053-001R1', N'Henry Mujica', N'NA', 2, N'Clientes Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (11, N'Revit ', N'2025', N'2025-12-05', N'2026-12-05', N'574-60008874', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (12, N'Revit ', N'2025', N'2025-12-05', N'2026-12-05', N'574-73836720', N'Henry Mujica', N'NA', 2, N'Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (13, N'Revit ', N'2025', N'2025-09-01', N'2026-09-01', N'Subscription', N'alirio.rojas@gmail.com', N'NA', 2, N'Cuenta de Alirio')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (14, N'McFee', N'Profesional', N'2025-12-01', N'2026-12-01', N'Subscription', N'Victor Valencia ', N'NA', 2, N'Se instalo Bluebeam y McFee
ahi que borrar la tarjeta de Credito de McFee')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (15, N'Revit ', N'2025', N'2026-01-01', N'2026-05-05', N'575-07754749', N'manueledu22@gmail.com/Manuel Jimenez', N'NA', 2, N'Se asigno la Licencia 575-07754749, pero no funciono. se cambio por subscripcion hay que recordar al proveedor cada 3 meses')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (16, N'Revit ', N'2025', N'2026-03-10', N'2027-03-10', N'vilchezwm@gmail.com', N'Wilhired Vilchez', N'NA', 2, N'Se habia instalado La Licencia con el Serial Number: 575-46607110, pero no funciono se instalo con proveedor y hay que renovar cada 3 meses ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (17, N'AutoCAD ', N'2026', N'2025-12-01', N'2026-12-01', N'jony_romo@hotmail.com', N'Andy Romo', N'NA', 2, N'Licencia por subscripcion ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (18, N'Windows ', N'11 Pro', N'2025-12-01', N'2030-12-31', N'9X4N6-W26CD-3MK3M-6VK4R-7H66T', N'Roby Romo RLS', N'NA', 2, N'Licencia W11 Pro Roberto Romo')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (19, N'McFee', N'Antivirus Plus', N'2026-05-27', N'2027-05-27', N'Subscription', N'info@devromo.com', N'NA', 2, N'Antivirys McFee
Activo en computadora personal,
Roby, Aryanna, Andy')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (20, N'ZerosSSL', N'Certificado SSL', N'2026-01-01', N'2027-01-01', N'Subscription', N'eliasvillegazcruz@gmail.com', N'NA', 2, N'Cuenta que hay que pagar anualmente con Elias')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (25, N'Godaddy', N'Webpage RLS', N'2026-01-27', N'2027-01-27', N'Subscripcion', N'andy@romolifesafety.com', N'NA', 2, N'Cobro Anual Webpage: Dominio Certificado SSL, Hoting, Codigo QR ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (29, N'Godaddy ', N'Webpage SWG', N'2026-02-01', N'2027-02-01', N'Subscription', N'speedygonzalezwelding@gmail.com', N'NA', 2, N'Webpage: Hosting, Certificado SSL, (dominio) lo tiene en m365')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (30, N'Godaddy', N'Webpage La Masajista', N'2025-06-01', N'2026-06-01', N'Subscription', N'licensedmassagepros@gmail.com', N'NA', 2, N'Webpage: Dominio, Certificado SSL, QR y Hosting')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (33, N'Antivirus ', N'Trend maximum 3D', N'2023-09-09', N'2026-09-26', N'XRMQ-0013-9700-4517-504', N'Alejandro SEDE ', N'NA', 2, N'Licencia Antivirus Alejandro clínica SEDE ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (34, N'Godaddy', N'Webpage Havana NRNG', N'2025-08-01', N'2026-08-01', N'Subscription', N'havananrgbookings@gmail.com', N'NA', 2, N'Webpage: Havana NRG, Dominio, Certificado SSL, Código QR, Hosting ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (35, N'Windows ', N'11 Pro', N'2026-01-28', N'2039-12-31', N'RNHDG-JMWXP-RQCH6-FTRKX-V22KG', N'Info@romolifesafety.com', N'NA', 2, N'Licencia de Aryanna de RLS')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (36, N'AutoCAD ', N'2026', N'2026-02-19', N'2027-02-19', N'575-51419614-001R1', N'Henry Mujica', N'Na', 2, N'Licencia a Henry Mujica AutoCAD 2026 1 año, se cambio por una licencia de subscripcion')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (37, N'Revit ', N'Revit Subscription', N'2026-02-20', N'2027-02-20', N'ybuitragov@gmail.com', N'Henri Mujica', N'NA', 2, N'Licencia de Cliente de Henry Mujica')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (38, N'Revit ', N'2026', N'2026-02-26', N'2027-02-26', N'Subscription ', N'trossell5@gmail.com', N'NA', 2, N'Licencia de Henry Mujica ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (39, N'AutoCAD ', N'2025', N'2026-03-02', N'2027-02-22', N'575-50292219:001Q1', N'Oscar CA Services ', N'NA', 2, N'Licencia a Oscar pago la de 3 años pero solo se activo por un año el key tambien se instalo Sketchup')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (40, N'Surfshark ', N'VPN', N'2026-08-15', N'2027-08-15', N'Subscription Trial ', N'Jony.romo001@gmail.com', N'NA', 2, N'Subscripcion de Prueba ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (41, N'Revit ', N'2026', N'2026-03-10', N'2027-03-10', N'Sibscription', N'montanezcristian@gmail.com', N'NA', 2, N'Licencia de Cristian Montanez, tiene 2 dispositivos en Revit y uno de AutoCAD que vence el 28 de abril licencia 575-21731360, y la de Autocad el 10 de Marzo')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (42, N'Revit', N'2025', N'2026-03-08', N'2027-03-08', N'Na', N'frankmhg@outlook.com', N'Na', 2, N'Licencia de Frank Hidalgo ')
INSERT [dbo].[licenses] ([license_id], [software], [version], [created_at], [expiry_date], [key], [account], [password], [employee_id], [notes]) VALUES (43, N'Office 2024 LTSC', N'2024', N'2026-04-17', N'2039-12-31', N'7YJKT-NW9T6-YP2XB-TWH4C-DDFPW', N'Juan Arqutiecto', N'NA', 2, N'Licencia Office perpetua ')

SET IDENTITY_INSERT [dbo].[licenses] OFF
GO


-- Data for modules (17 records)
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
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (13, N'Hardware', N'hardware', N'Modulo para gestionar inventario de equipos de cómputo', N'settings', N'/hardware', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'', N'/time-off/calendar', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (16, N'customers', N'customers', N'customers', N'customers', N'customers', 0, 1, NULL, '2026-01-29 05:13:51')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (17, N'products', N'products', N'Module to handle products for proposals', N'', N'/products', 15, 1, 16, '2026-02-14 19:00:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (18, N'Timesheet', N'timesheet', N'timesheet', N'', N'/timesheet', 0, 1, NULL, '2026-02-26 03:19:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (19, N'Quotations', N'quotations', N'Module to create quotations to a existing or new customers', N'', N'/quotations', 19, 1, 16, '2026-03-07 11:32:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (20, N'Inventory Overview', N'Inventory', N'Module to handle all Inventory related operations', NULL, N'/inventory/overview', 20, 1, NULL, '2026-05-10 17:29:59')

SET IDENTITY_INSERT [dbo].[modules] OFF
GO


-- product_families: No data to insert


-- product_categories: No data to insert


-- Data for quotations (2 records)
SET IDENTITY_INSERT [dbo].[quotations] ON
GO

INSERT [dbo].[quotations] ([id], [customer_id], [quote_date], [expiration_date], [subtotal], [tax], [discount], [total], [status], [notes], [created_at]) VALUES (1, 3, N'2026-03-22 00:30:55.9300000', N'2026-04-21 00:30:55.9300000', '12.00', '0.00', '0.00', '12.00', N'Draft', N'Quotation for Andy', N'2026-03-22 00:34:15.0262100')
INSERT [dbo].[quotations] ([id], [customer_id], [quote_date], [expiration_date], [subtotal], [tax], [discount], [total], [status], [notes], [created_at]) VALUES (2, 3, N'2026-04-12 17:36:32.5390000', N'2026-05-12 17:36:32.5390000', '5.00', '0.00', '0.00', '5.00', N'Draft', N'quotation test', N'2026-04-12 17:54:48.9380990')

SET IDENTITY_INSERT [dbo].[quotations] OFF
GO


-- quotation_items: No data to insert


-- Data for role_modules (32 records)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 1, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 3, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 5, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 6, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 7, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 8, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 10, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 11, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 12, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 13, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 14, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 15, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 16, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 17, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 18, 1, 1, 1, 1, 1, 1, 1, '2026-02-26 03:20:08')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 19, 1, 1, 1, 1, 1, 1, 1, '2026-03-07 11:59:33')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 20, 1, 1, 1, 1, 1, 1, 1, '2026-05-10 17:31:25')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (2, 3, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (2, 14, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 12, 1, 1, 1, 1, 1, 0, 0, '2025-12-13 16:58:09')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 1, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 3, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 5, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 6, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:43')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 7, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 8, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 10, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:44')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 11, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 12, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 13, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:45')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 14, 0, 0, 0, 0, 0, 0, 0, '2025-12-28 05:40:42')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (8, 15, 1, 1, 1, 1, 1, 1, 1, '2025-12-28 05:40:41')
GO


-- Data for tenant_employees (6 records)
SET IDENTITY_INSERT [dbo].[tenant_employees] ON
GO

INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (2, 1, '2026-01-25 19:15:18', N'jcarlos.villa.rivera@gmail.com', N'$2b$12$cDUo.dcX2PsVu3QN.USy6eB0CNBgIs4oylaXh8hceQDgUgn79xLYW')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (4, 1, '2026-02-12 01:48:20', N'info@devromo.com', N'$2b$12$gi3XmKKpzRR9ykeM4hRMXOapq3xlqHKI1ruFgrU7/EepRcG72Zrs6')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (5, 1, '2026-03-05 04:00:10', N'javiermendozar73@gmail.com', N'$2b$12$5BBcHMjwPW4SygLgge2Z6uY8eHthHOuigMPf7X8CQV3xGrCD1UQQ2')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (6, 1, '2026-03-12 23:51:03', N'jony.romo001@gmail.com', N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (7, NULL, '2026-06-04 16:38:14', N'mordaz@primefire.us', N'$2b$12$/Til07oiYpI0gvC.BcUMouu9qg3/nhQHqgcDw.RyHVvbUsrW1RNDG')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (8, 1, '2026-06-07 04:58:08', N'mordaz@devromo.com', N'$2b$12$ePWR0datxEHIJBVIMQpA5elEQ02aZ9jig4zQ3OD92IFPWW1MsGrZ2')

SET IDENTITY_INSERT [dbo].[tenant_employees] OFF
GO


-- Data for tenant_logos (2 records)
SET IDENTITY_INSERT [dbo].[tenant_logos] ON
GO

INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email]) VALUES (1, 1, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com', N'assets/fav/devromo.webp', NULL)
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email]) VALUES (2, 1, N'Developer''s Romo Local', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', '2026-01-25 19:41:43', N'localhost:4201', N'assets/fav/devromo.webp', NULL)

SET IDENTITY_INSERT [dbo].[tenant_logos] OFF
GO


-- Data for tickets (8 records)
SET IDENTITY_INSERT [dbo].[tickets] ON
GO

INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (1, N'Outlook Faailure', N'Outlook no funcionan Correectamente ', N'closed', N'normal', N'1h', 2, 2, N'2026-06-04 16:44:45.0000000', N'2026-06-04 16:44:53.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (2, N'Certificados SSL ', N'cambiar los certificados SSL de las siguientes paginas: RLS, SGW, Havana NRG, LicensedMassagePros, PrimeFire', N'todo', N'high', N'4h', 2, 200, N'2026-06-07 05:49:26.0000000', N'2026-06-07 05:49:26.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (3, N'Calendar Excel ', N'Ajustar el Excel Vacations para los empleados RomoLifeSafety', N'todo', N'normal', N'8h', 2, 200, N'2026-06-07 05:52:43.0000000', N'2026-06-07 05:52:43.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (4, N'Agregar Hardware & Software a Inventario & Cambiar a Dominio Devromo', N'Agregar Software & hardware a Inventario app.devromo', N'todo', N'normal', N'4h', 2, 200, N'2026-06-07 05:55:50.0000000', N'2026-06-07 05:55:50.0000000', N'improvement', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (5, N'Agregar Eventos Havana NRG ', N'Cada 1 de cada Mes agregar los eventos de Havana NRG ', N'todo', N'normal', N'1h', 2, 200, N'2026-06-07 05:57:12.0000000', N'2026-06-07 05:57:12.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (6, N'Agregar a Inventario cada 1 de las Maquinas RLS ', N'Agregar al inventario cada uno de los dispositivos de RLS y asegurar que tengan la licencia Microsoft Windows Pro; también meterlos a dominio. ', N'todo', N'normal', N'1h', 2, 200, N'2026-06-07 06:01:25.0000000', N'2026-06-07 06:01:25.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (7, N'habilitar usuarios de RLS a la aplicacion ', N'Habilitar a: 
Alex Romo,
Andres Romo,
Ariana Gomez,
Jose Nieto,
Matias Morales,
Mireya Gomez,
Monica Cruz, 
Roberto Romo, todos con el role de Excepto Mireya, Andy y Roberto como Managers', N'todo', N'normal', N'8h', 2, 200, N'2026-06-07 06:13:50.0000000', N'2026-06-07 06:14:41.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (8, N'Homologar Iconos con PrimeFire', N'Homologar los iconos de la app Primefire', N'todo', N'low', N'1h', 2, 200, N'2026-06-07 06:16:29.0000000', N'2026-06-07 06:16:29.0000000', N'request', NULL)

SET IDENTITY_INSERT [dbo].[tickets] OFF
GO


-- ticket_messages: No data to insert


-- ticket_attachments: No data to insert


-- Data for ticket_recurrence_config (2 records)
SET IDENTITY_INSERT [dbo].[ticket_recurrence_config] ON
GO

INSERT [dbo].[ticket_recurrence_config] ([config_id], [ticket_id], [recurrence_type], [next_occurrence], [parent_ticket_id], [is_active], [created_at]) VALUES (1, 2, N'BIMONTHLY', N'2026-08-07 05:49:26.0000000', NULL, 1, N'2026-06-07 05:49:26.0000000')
INSERT [dbo].[ticket_recurrence_config] ([config_id], [ticket_id], [recurrence_type], [next_occurrence], [parent_ticket_id], [is_active], [created_at]) VALUES (2, 5, N'MONTHLY', N'2026-07-07 05:57:13.0000000', NULL, 1, N'2026-06-07 05:57:13.0000000')

SET IDENTITY_INSERT [dbo].[ticket_recurrence_config] OFF
GO


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


-- Data for time_sheet_location_snapshots (14 records)
SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] ON
GO

INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (1, 2, 4, N'201.172.175.223:55079', N'25.76918114892164', N'-100.45507686092162', N'10.750824078150503', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-04-27 11:46:14')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (2, 2, 4, N'201.172.175.223:57696', N'25.769180631319543', N'-100.45507778548088', N'19.97672002939698', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-04-27 22:49:16')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (3, 2, 4, N'201.172.175.223:65203', N'25.76918099126356', N'-100.4550782802133', N'8.404800947120567', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-04-29 11:50:26')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (4, 2, 4, N'200.68.165.1:13909', N'25.720069771114918', N'-100.52828283346446', N'8.05506678594521', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-04-29 21:50:40')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (5, 2, 4, N'201.162.167.83:23207', N'28.67394373138481', N'-99.18231820839166', N'62', NULL, NULL, NULL, N'America/Chicago', NULL, N'2026-05-01 17:43:29')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (6, 2, 4, N'201.166.169.59:11969', N'25.658858645986818', N'-100.44236742630581', N'5.996698425624708', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-04 17:38:50')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (7, 2, 4, N'103.88.234.35:55538', N'25.769204702719044', N'-100.45508278514598', N'7.274828151286745', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-05 13:37:32')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (8, 2, 4, N'103.88.234.191:54452', N'25.76918736693643', N'-100.45507510762806', N'11.037352883302603', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-06 04:01:51')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (9, 2, 4, N'103.88.234.101:42498', N'25.769221275341938', N'-100.4550881395232', N'9.472995453386407', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-11 11:50:51')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (10, 2, 4, N'201.172.175.223:54594', N'25.769202348003386', N'-100.45510465368353', N'7.2580037964583575', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-12 11:50:53')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (11, 2, 4, N'201.172.175.223:54497', N'25.769203606793457', N'-100.4551026175349', N'7.744713461772746', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-13 02:00:00')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (12, 2, 4, N'201.172.175.223:58563', N'25.76920387478592', N'-100.45510192448857', N'6.833188224078922', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-13 11:51:00')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (13, 2, 4, N'212.102.40.84:57346', N'25.719811058612493', N'-100.53219396624112', N'8.435733951689471', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-15 14:12:33')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (14, 2, 4, N'212.102.40.84:57346', N'25.719811058612493', N'-100.53219396624112', N'8.435733951689471', NULL, NULL, NULL, N'America/Monterrey', NULL, N'2026-05-15 14:12:49')

SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] OFF
GO


-- Data for time_sheet_punches (10 records)
SET IDENTITY_INSERT [dbo].[time_sheet_punches] ON
GO

INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (1, 2, 4, N'2026-04-27 11:46:15', N'2026-04-27 22:49:17', N'America/Monterrey', NULL, N'25.769180631319543', N'-100.45507778548088', N'19.97672002939698', NULL, NULL, NULL, NULL, 663, N'closed', NULL, NULL, NULL, N'2026-04-27 11:46:15', N'2026-04-27 22:49:17')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (2, 2, 4, N'2026-04-29 11:50:26', N'2026-04-29 21:50:41', N'America/Monterrey', NULL, N'25.720069771114918', N'-100.52828283346446', N'8.05506678594521', NULL, NULL, NULL, NULL, 600, N'closed', NULL, NULL, NULL, N'2026-04-29 11:50:26', N'2026-04-29 21:50:41')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (3, 2, 4, N'2026-05-01 17:43:30', N'2026-05-04 17:38:40', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 4315, N'closed', NULL, NULL, NULL, N'2026-05-01 17:43:30', N'2026-05-04 17:38:40')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (4, 2, 4, N'2026-05-04 17:38:50', N'2026-05-05 13:37:00', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1198, N'closed', NULL, NULL, NULL, N'2026-05-04 17:38:50', N'2026-05-05 13:37:00')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (5, 2, 4, N'2026-05-05 13:37:33', N'2026-05-06 04:01:51', N'America/Monterrey', NULL, N'25.76918736693643', N'-100.45507510762806', N'11.037352883302603', NULL, NULL, NULL, NULL, 864, N'closed', NULL, NULL, NULL, N'2026-05-05 13:37:33', N'2026-05-06 04:01:51')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (6, 2, 4, N'2026-05-11 11:50:52', N'2026-05-12 11:50:51', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1439, N'closed', NULL, NULL, NULL, N'2026-05-11 11:50:52', N'2026-05-12 11:50:51')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (7, 2, 4, N'2026-05-12 11:50:54', N'2026-05-13 02:00:01', N'America/Monterrey', NULL, N'25.769203606793457', N'-100.4551026175349', N'7.744713461772746', NULL, NULL, NULL, NULL, 849, N'closed', NULL, NULL, NULL, N'2026-05-12 11:50:54', N'2026-05-13 02:00:01')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (8, 2, 4, N'2026-05-13 11:51:01', N'2026-05-15 14:12:28', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 3021, N'closed', NULL, NULL, NULL, N'2026-05-13 11:51:01', N'2026-05-15 14:12:28')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (9, 2, 4, N'2026-05-15 14:12:34', N'2026-05-15 14:12:38', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'closed', NULL, NULL, NULL, N'2026-05-15 14:12:34', N'2026-05-15 14:12:38')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (10, 2, 4, N'2026-05-15 14:12:49', N'2026-05-15 14:12:58', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'closed', NULL, NULL, NULL, N'2026-05-15 14:12:49', N'2026-05-15 14:12:58')

SET IDENTITY_INSERT [dbo].[time_sheet_punches] OFF
GO


-- Data for time_sheet_settings (1 records)
SET IDENTITY_INSERT [dbo].[time_sheet_settings] ON
GO

INSERT [dbo].[time_sheet_settings] ([setting_id], [overtime_daily_hours], [overtime_weekly_hours], [round_to_minutes], [is_active], [created_at], [updated_at], [max_overtime_daily_hours]) VALUES (1, N'8.00', N'40.00', NULL, 1, N'2026-04-26 00:02:28', N'2026-04-26 00:02:28', N'8.00')

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

ALTER TABLE [dbo].[inventory_movements] WITH CHECK ADD CONSTRAINT [FK_inventory_movements_products]
FOREIGN KEY([product_id])
REFERENCES [dbo].[products] ([id])
GO
ALTER TABLE [dbo].[inventory_movements] CHECK CONSTRAINT [FK_inventory_movements_products]
GO

ALTER TABLE [dbo].[inventory_movements] WITH CHECK ADD CONSTRAINT [FK_inventory_movements_warehouses]
FOREIGN KEY([warehouse_id])
REFERENCES [dbo].[warehouses] ([warehouse_id])
GO
ALTER TABLE [dbo].[inventory_movements] CHECK CONSTRAINT [FK_inventory_movements_warehouses]
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

ALTER TABLE [dbo].[product_categories] WITH CHECK ADD CONSTRAINT [FK__product_c__famil__7226EDCC]
FOREIGN KEY([family_id])
REFERENCES [dbo].[product_families] ([id])
GO
ALTER TABLE [dbo].[product_categories] CHECK CONSTRAINT [FK__product_c__famil__7226EDCC]
GO

ALTER TABLE [dbo].[quotation_items] WITH CHECK ADD CONSTRAINT [fk_quotation_items_quotation]
FOREIGN KEY([quotation_id])
REFERENCES [dbo].[quotations] ([id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[quotation_items] CHECK CONSTRAINT [fk_quotation_items_quotation]
GO

ALTER TABLE [dbo].[quotation_items] WITH CHECK ADD CONSTRAINT [fk_quotation_items_product]
FOREIGN KEY([product_id])
REFERENCES [dbo].[products] ([id])
GO
ALTER TABLE [dbo].[quotation_items] CHECK CONSTRAINT [fk_quotation_items_product]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [fk_quotations_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [fk_quotations_customers]
GO

ALTER TABLE [dbo].[role_modules] WITH CHECK ADD CONSTRAINT [fk_role_modul_role_i_20acd28b]
FOREIGN KEY([role_id])
REFERENCES [dbo].[roles] ([role_id])
GO
ALTER TABLE [dbo].[role_modules] CHECK CONSTRAINT [fk_role_modul_role_i_20acd28b]
GO

ALTER TABLE [dbo].[role_modules] WITH CHECK ADD CONSTRAINT [fk_role_modul_modul_21a0f6c4]
FOREIGN KEY([module_id])
REFERENCES [dbo].[modules] ([module_id])
GO
ALTER TABLE [dbo].[role_modules] CHECK CONSTRAINT [fk_role_modul_modul_21a0f6c4]
GO

ALTER TABLE [dbo].[ticket_attachments] WITH CHECK ADD CONSTRAINT [fk_ticket_att_ticke_2fef161b]
FOREIGN KEY([ticket_id])
REFERENCES [dbo].[tickets] ([ticket_id])
GO
ALTER TABLE [dbo].[ticket_attachments] CHECK CONSTRAINT [fk_ticket_att_ticke_2fef161b]
GO

ALTER TABLE [dbo].[ticket_attachments] WITH CHECK ADD CONSTRAINT [fk_ticket_att_ticke_30e33a54]
FOREIGN KEY([ticket_message_id])
REFERENCES [dbo].[ticket_messages] ([ticket_message_id])
GO
ALTER TABLE [dbo].[ticket_attachments] CHECK CONSTRAINT [fk_ticket_att_ticke_30e33a54]
GO

ALTER TABLE [dbo].[ticket_messages] WITH CHECK ADD CONSTRAINT [fk_ticket_mes_ticke_2c1e8537]
FOREIGN KEY([ticket_id])
REFERENCES [dbo].[tickets] ([ticket_id])
GO
ALTER TABLE [dbo].[ticket_messages] CHECK CONSTRAINT [fk_ticket_mes_ticke_2c1e8537]
GO

ALTER TABLE [dbo].[ticket_messages] WITH CHECK ADD CONSTRAINT [fk_ticket_mes_user_i_2d12a970]
FOREIGN KEY([user_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[ticket_messages] CHECK CONSTRAINT [fk_ticket_mes_user_i_2d12a970]
GO

ALTER TABLE [dbo].[ticket_recurrence_config] WITH CHECK ADD CONSTRAINT [FK_ticket_recurrence_config_tickets]
FOREIGN KEY([ticket_id])
REFERENCES [dbo].[tickets] ([ticket_id])
ON DELETE SET NULL
GO
ALTER TABLE [dbo].[ticket_recurrence_config] CHECK CONSTRAINT [FK_ticket_recurrence_config_tickets]
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

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [fk_time_sheet_emplo_31b762fc]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [fk_time_sheet_emplo_31b762fc]
GO

ALTER TABLE [dbo].[time_sheet_location_snapshots] WITH CHECK ADD CONSTRAINT [fk_time_sheet_custo_32ab8735]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_location_snapshots] CHECK CONSTRAINT [fk_time_sheet_custo_32ab8735]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_emplo_2cf2addf]
FOREIGN KEY([employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_emplo_2cf2addf]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_custo_2de6d218]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_custo_2de6d218]
GO

ALTER TABLE [dbo].[time_sheet_punches] WITH CHECK ADD CONSTRAINT [fk_time_sheet_appro_2edaf651]
FOREIGN KEY([approved_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[time_sheet_punches] CHECK CONSTRAINT [fk_time_sheet_appro_2edaf651]
GO

ALTER TABLE [dbo].[warehouses] WITH CHECK ADD CONSTRAINT [FK_warehouses_warehouse_locations_location_id]
FOREIGN KEY([location_id])
REFERENCES [dbo].[warehouse_locations] ([warehouse_location_id])
GO
ALTER TABLE [dbo].[warehouses] CHECK CONSTRAINT [FK_warehouses_warehouse_locations_location_id]
GO


-- =============================================
-- BACKUP SUMMARY
-- =============================================
-- Backup Type: FULL
-- Total Tables: 39
-- Total Records: 195
-- 
-- Data per table:
--   countries: 5 records
--   addresses: 7 records
--   auth_tokens: 18 records
--   employees: 4 records
--   customers: 5 records
--   roles: 5 records
--   employee_roles: 4 records
--   tenants: 1 records
--   hardware_inventory: 2 records
--   products: 6 records
--   warehouses: 1 records
--   inventory_movements: 2 records
--   licenses: 34 records
--   modules: 17 records
--   quotations: 2 records
--   role_modules: 32 records
--   tenant_employees: 6 records
--   tenant_logos: 2 records
--   tickets: 8 records
--   ticket_recurrence_config: 2 records
--   time_off_balances: 4 records
--   time_off_requests: 3 records
--   time_sheet_location_snapshots: 14 records
--   time_sheet_punches: 10 records
--   time_sheet_settings: 1 records
-- =============================================

PRINT 'Backup restored successfully!'
PRINT 'Total records inserted: 195'
GO
