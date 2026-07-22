USE [devromo]
GO

/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/
/****** Generated: 2026-07-21 15:24:11 ******/
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

IF OBJECT_ID('dbo.product_specifications', 'U') IS NOT NULL
    DROP TABLE dbo.product_specifications;
GO

IF OBJECT_ID('dbo.product_families', 'U') IS NOT NULL
    DROP TABLE dbo.product_families;
GO

IF OBJECT_ID('dbo.product_categories', 'U') IS NOT NULL
    DROP TABLE dbo.product_categories;
GO

IF OBJECT_ID('dbo.product_catalog', 'U') IS NOT NULL
    DROP TABLE dbo.product_catalog;
GO

IF OBJECT_ID('dbo.product_attachments', 'U') IS NOT NULL
    DROP TABLE dbo.product_attachments;
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

IF OBJECT_ID('dbo.inventory_movement_approvals', 'U') IS NOT NULL
    DROP TABLE dbo.inventory_movement_approvals;
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
-- Table: inventory_movement_approvals
-- =============================================

CREATE TABLE [dbo].[inventory_movement_approvals](
    [approval_id] [int] IDENTITY(1,1) NOT NULL,
    [product_id] [int] NOT NULL,
    [warehouse_id] [int] NULL,
    [movement_type] [varchar](20) NOT NULL,
    [quantity] [decimal](18,2) NOT NULL,
    [movement_date] [date] NOT NULL DEFAULT (CONVERT([date],getdate())),
    [project] [nvarchar](150) NULL,
    [po_number] [nvarchar](100) NULL,
    [reference_type] [nvarchar](50) NULL,
    [reference_id] [int] NULL,
    [notes] [nvarchar](500) NULL,
    [status] [varchar](20) NOT NULL DEFAULT ('PENDING'),
    [requested_by] [nvarchar](100) NULL,
    [requested_by_email] [nvarchar](255) NULL,
    [review_note] [nvarchar](500) NULL,
    [reviewed_by] [nvarchar](100) NULL,
    [reviewed_at] [datetime2] NULL,
    [movement_id] [int] NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (getdate()),
 CONSTRAINT [PK_inventory_movement_approvals] PRIMARY KEY CLUSTERED
(
    [approval_id] ASC
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
-- Table: product_attachments
-- =============================================

CREATE TABLE [dbo].[product_attachments](
    [product_attachment_id] [int] IDENTITY(1,1) NOT NULL,
    [product_id] [int] NOT NULL,
    [file_name] [varchar](255) NOT NULL,
    [file_type] [varchar](100) NULL,
    [file_path] [varchar](500) NULL,
    [created_at] [datetime] NOT NULL,
    [created_by] [int] NOT NULL,
 CONSTRAINT [PK__product___EAF11C229B352418] PRIMARY KEY CLUSTERED
(
    [product_attachment_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: product_catalog
-- =============================================

CREATE TABLE [dbo].[product_catalog](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [code] [varchar](50) NOT NULL,
    [name] [varchar](255) NOT NULL,
    [family_id] [int] NULL,
    [category_id] [int] NULL,
    [unit] [varchar](20) NULL,
    [min_stock] [numeric](12,2) NOT NULL,
    [active] [bit] NOT NULL,
    [description] [varchar](MAX) NULL,
    [created_at] [datetime] NOT NULL,
 CONSTRAINT [PK__product___3213E83FBA6D4BF3] PRIMARY KEY CLUSTERED
(
    [id] ASC
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
 CONSTRAINT [PK__product___3213E83FB2F54A46] PRIMARY KEY CLUSTERED
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
    [created_at] [datetime] NOT NULL DEFAULT (sysutcdatetime()),
 CONSTRAINT [PK__product___3213E83FF681DC5A] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: product_specifications
-- =============================================

CREATE TABLE [dbo].[product_specifications](
    [id] [int] IDENTITY(1,1) NOT NULL,
    [product_id] [int] NOT NULL,
    [specification] [varchar](100) NULL,
    [size] [varchar](100) NULL,
    [material] [varchar](100) NULL,
    [manufacturer] [varchar](100) NULL,
    [model] [varchar](100) NULL,
    [notes] [varchar](MAX) NULL,
 CONSTRAINT [PK__product___3213E83F29566D85] PRIMARY KEY CLUSTERED
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
    [family_id] [int] NULL,
    [category_id] [int] NULL,
    [specification] [nvarchar](100) NULL,
    [manufacturer] [nvarchar](100) NULL,
    [model] [nvarchar](100) NULL,
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
    [quotation_item_id] [int] NOT NULL,
    [id] [int] IDENTITY(1,1) NOT NULL,
    [quotation_id] [int] NOT NULL,
    [quotation_id] [int] NOT NULL,
    [catalog_item_id] [int] NULL,
    [product_id] [int] NOT NULL,
    [description] [nvarchar](1000) NULL,
    [item_type] [varchar](30) NOT NULL,
    [billing_cycle] [varchar](20) NOT NULL,
    [quantity] [decimal](18,2) NOT NULL DEFAULT ((1)),
    [unit_price] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [code_snapshot] [nvarchar](100) NULL,
    [name_snapshot] [nvarchar](200) NOT NULL,
    [discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [description_snapshot] [nvarchar](2000) NULL,
    [scope_snapshot] [nvarchar](MAX) NULL,
    [total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [quantity] [decimal](18,2) NOT NULL DEFAULT ((1)),
    [unit] [nvarchar](50) NOT NULL DEFAULT ('EA'),
    [unit_price] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [discount_percent] [decimal](5,2) NOT NULL DEFAULT ((0)),
    [tax_rate] [decimal](5,2) NOT NULL DEFAULT ((0)),
    [line_subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [line_discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [line_tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [line_total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [term_months] [int] NULL,
    [sort_order] [int] NOT NULL DEFAULT ((0)),
 CONSTRAINT [PK__quotatio__0A84FFE7EFB5B802] PRIMARY KEY CLUSTERED
(
    [quotation_item_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

-- =============================================
-- Table: quotations
-- =============================================

CREATE TABLE [dbo].[quotations](
    [quotation_id] [int] NOT NULL,
    [id] [int] IDENTITY(1,1) NOT NULL,
    [customer_id] [int] NOT NULL,
    [tenant_id] [int] NOT NULL,
    [customer_id] [int] NOT NULL,
    [quote_date] [datetime2] NOT NULL DEFAULT (sysdatetime()),
    [expiration_date] [datetime2] NULL,
    [contact_id] [int] NULL,
    [quotation_number] [nvarchar](50) NOT NULL,
    [subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [status] [varchar](30) NOT NULL DEFAULT ('DRAFT'),
    [quote_date] [date] NOT NULL,
    [discount] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [expiration_date] [date] NOT NULL,
    [currency] [char](3) NOT NULL DEFAULT ('USD'),
    [status] [varchar](20) NOT NULL DEFAULT ('Draft'),
    [notes] [nvarchar](2000) NULL,
    [customer_name_snapshot] [nvarchar](200) NOT NULL,
    [contact_name_snapshot] [nvarchar](200) NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysdatetime()),
    [customer_email_snapshot] [nvarchar](200) NULL,
    [customer_address_snapshot] [nvarchar](1000) NULL,
    [one_time_subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [monthly_recurring_subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [annual_recurring_subtotal] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [discount_total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [tax_total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [initial_total] [decimal](18,2) NOT NULL DEFAULT ((0)),
    [visible_notes] [nvarchar](MAX) NULL,
    [internal_notes] [nvarchar](MAX) NULL,
    [template_id] [int] NULL,
    [owner_employee_id] [int] NULL,
    [created_by] [int] NULL,
    [created_at] [datetime2] NOT NULL DEFAULT (sysutcdatetime()),
    [updated_at] [datetime2] NULL,
    [sent_at] [datetime2] NULL,
    [accepted_at] [datetime2] NULL,
    [rejected_at] [datetime2] NULL,
    [row_version] [timestamp] NOT NULL,
 CONSTRAINT [PK__quotatio__7841D7DB7EE77AB3] PRIMARY KEY CLUSTERED
(
    [quotation_id] ASC
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
    [auth_provider] [varchar](20) NOT NULL DEFAULT ('password'),
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


-- Data for auth_tokens (22 records)
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
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (19, N'jcarlos.villa.rivera@gmail.com', N'W3W_1WND0LVn0NT-Hvyry4-ZqmKMfMJ2ER1SUlAfObk', N'password_recovery', N'2026-06-11 03:03:01.663333', N'2026-06-11 02:51:48.539885', N'2026-06-11 02:48:01.663333')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (20, N'jcarlos.villa.rivera@gmail.com', N'LQ_ubShOQZ9I7uctqYemf7gkVJsmSLBKMzE_0xrupDU', N'password_recovery', N'2026-06-24 04:03:08.557385', N'2026-07-16 21:30:49.956489', N'2026-06-24 03:48:08.557559')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (21, N'jcarlos.villa.rivera@gmail.com', N'wIaSIJgtuNd2WokR_D25OjSKehGsN6ZCpuv6MHMml5U', N'magic_link', N'2026-07-16 21:45:10.952580', NULL, N'2026-07-16 21:30:10.958435')
INSERT [dbo].[auth_tokens] ([id], [email], [token], [token_type], [expires_at], [used_at], [created_at]) VALUES (22, N'jcarlos.villa.rivera@gmail.com', N'5wvx4s4YPf2wT6Rh6nHoeKLOKIkG0wWMg1pHeDwpVgE', N'password_recovery', N'2026-07-16 21:45:50.016816', NULL, N'2026-07-16 21:30:50.017007')

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


-- Data for customer_alternate_contacts (1 records)
SET IDENTITY_INSERT [dbo].[customer_alternate_contacts] ON
GO

INSERT [dbo].[customer_alternate_contacts] ([customer_alternate_contact_id], [customer_id], [name], [email], [phone], [created_at], [updated_at]) VALUES (1, 4, N'test', N'test@tyest.com', N'1231231232', N'2026-07-18 23:41:34.0000000', NULL)

SET IDENTITY_INSERT [dbo].[customer_alternate_contacts] OFF
GO


-- customer_attachments: No data to insert


-- customer_notes: No data to insert


-- departments: No data to insert


-- Data for roles (6 records)
SET IDENTITY_INSERT [dbo].[roles] ON
GO

INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (1, N'Admin', N'System Administrator with full access')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (2, N'Manager', N'Department manager with elevated permissions')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (3, N'User', N'Standard user with basic access')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (5, N'Jobs ', N'Administrador modulo Jobs')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (8, N'Admin_Tenants', N'Tenants')
INSERT [dbo].[roles] ([role_id], [role_name], [description]) VALUES (9, N'Beta_Tester', N'Grants access to selected in-development or preview features before they are generally available.')

SET IDENTITY_INSERT [dbo].[roles] OFF
GO


-- Data for employee_roles (6 records)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (1, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 1)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 2)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (2, 3)
INSERT [dbo].[employee_roles] ([employee_id], [role_id]) VALUES (200, 1)
GO


-- Data for tenants (2 records)
SET IDENTITY_INSERT [dbo].[tenants] ON
GO

INSERT [dbo].[tenants] ([tenant_id], [name], [db_connection_key], [description], [is_active], [created_at]) VALUES (1, N'DevRomo', N'MAIN', N'Developer''s Romo', 1, '2026-01-25 18:49:45')
INSERT [dbo].[tenants] ([tenant_id], [name], [db_connection_key], [description], [is_active], [created_at]) VALUES (2, N'PrimeFire', N'PRIMEFIRE', N'PrimeFire', 1, '2026-06-11 05:36:41')

SET IDENTITY_INSERT [dbo].[tenants] OFF
GO


-- external_users: No data to insert


-- Data for hardware_inventory (3 records)
SET IDENTITY_INSERT [dbo].[hardware_inventory] ON
GO

INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (3, N'6L7KQ73', N'Dell', N'Alienware ', N'Laptop', N'Intel Core(TM) i9-10900 CPU', NULL, N'NVMe', 954, NULL, N'Windows 11 Home', N'2023-01-01', N'2024-01-01', N'2023-01-01', 2, N'Grand Preire ', N'Active', N'Laptop de Backup', '2026-02-20 22:42:42', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (4, N'C9PN75X46D', N'Apple', N'MYWG3E/A', N'Other', N'A18 PRO', 20, N'SSD', 256, N'Apple 5 Nucleos', N'iOS', N'2025-03-14', N'2026-03-14', N'2025-03-14', 2, N'MTY', N'Active', N'Iphone Jonathan', '2026-04-03 06:48:18', NULL)
INSERT [dbo].[hardware_inventory] ([hardware_id], [serial_number], [brand], [model], [device_type], [processor], [ram_gb], [storage_type], [storage_size_gb], [gpu], [operating_system], [warranty_start_date], [warranty_end_date], [purchase_date], [employee_id], [location], [status], [notes], [created_at], [updated_at]) VALUES (7, N'K2511N0032830', N'MSI', N'Thin 15 B13V', N'Laptop', N'13th Gen Intel(R) Core(TM) i5-13420H (2.10 GHz)', 16, N'SSD', 512, N'NVIDIA GeForce RTX 4060 Laptop GPU (8 GB)', N'Windows 11 pro', N'2026-05-31', N'2027-05-31', N'2026-05-31', NULL, N'Monterrey', N'Active', N'Laptop Mario', '2026-06-18 14:52:18', '2026-06-23 00:00:00')

SET IDENTITY_INSERT [dbo].[hardware_inventory] OFF
GO


-- holidays: No data to insert


-- Data for product_families (4 records)
SET IDENTITY_INSERT [dbo].[product_families] ON
GO

INSERT [dbo].[product_families] ([id], [name], [description], [active], [created_at]) VALUES (5, N'Fire Alarm', NULL, 1, '2026-06-10 06:13:13')
INSERT [dbo].[product_families] ([id], [name], [description], [active], [created_at]) VALUES (6, N'Plumbing', NULL, 1, '2026-06-10 06:13:13')
INSERT [dbo].[product_families] ([id], [name], [description], [active], [created_at]) VALUES (7, N'Fire Sprinkler', NULL, 1, '2026-06-10 06:13:13')
INSERT [dbo].[product_families] ([id], [name], [description], [active], [created_at]) VALUES (8, N'Security', NULL, 1, '2026-06-10 06:13:13')

SET IDENTITY_INSERT [dbo].[product_families] OFF
GO


-- Data for product_categories (4 records)
SET IDENTITY_INSERT [dbo].[product_categories] ON
GO

INSERT [dbo].[product_categories] ([id], [family_id], [name], [description], [active]) VALUES (1, 5, N'Device', NULL, 1)
INSERT [dbo].[product_categories] ([id], [family_id], [name], [description], [active]) VALUES (2, 5, N'Module', NULL, 1)
INSERT [dbo].[product_categories] ([id], [family_id], [name], [description], [active]) VALUES (3, 6, N'Valve', NULL, 1)
INSERT [dbo].[product_categories] ([id], [family_id], [name], [description], [active]) VALUES (4, 7, N'Head', NULL, 1)

SET IDENTITY_INSERT [dbo].[product_categories] OFF
GO


-- Data for products (6 records)
SET IDENTITY_INSERT [dbo].[products] ON
GO

INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (11, N'Webpages & Marketing Digital', N'Package! For only $1200 to $1800, you''ll receive everything you need to establish a strong online presence for your business. Our package includes:
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
Analytics to track your website''s performance.', N'Service', N'NA', '1200.00', '1800.00', '16.00', N'licencia', 100, 1, N'2026-02-25 01:23:14.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (13, N'Single QR ', N'QR multiporpouse Marketing', N'Product', N'NA', '5.00', '49.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:26:38.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (14, N'2 QR''s', N'Multiporpouse QR''s Marketing', N'Product', N'NA', '7.00', '69.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:29:51.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (15, N'3 QR''s', N'Multiporpuse Marketing', N'Product', N'NA', '10.00', '99.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:30:48.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (16, N'Landing Page', N'A single page website, also known as a one-page website, is a type of web business card that consists of only one HTML page. Unlike a traditional website, which has multiple pages and navigation menus, a single page website displays all the essential information on a single scrolling page.
- It is more user-friendly and mobile-friendly, as it eliminates the need for clicking and loading new pages
- It is more focused and concise, as it forces you to prioritize the most vital information and messages
- It is more engaging and interactive, as it can use animations, transitions, and effects to create a seamless and immersive experience for the visitors', N'Service', N'NA', '450.00', '800.00', '16.00', N'licencia', 100, 1, N'2026-03-08 06:46:01.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[products] ([id], [name], [description], [type], [sku], [unit_price], [cost], [tax_rate], [unit], [stock_quantity], [is_active], [created_at], [code], [family], [category], [size], [material_type], [min_stock], [needed_quantity], [family_id], [category_id], [specification], [manufacturer], [model]) VALUES (17, N'Business cards + Digital QR', N'A web business card, also known as a digital business card, electronic business card, or virtual business card, is the modern take on the traditional paper business card.
Instead of being printed on physical cardstock, a web business card is a webpage containing your contact information and professional details. Like a website, it can be designed and customized to reflect your personal brand.
Here is a breakdown of how web business cards work:
•
Function: Like a paper card, it displays your name, job title, company affiliation, contact details (phone, email), and potentially a website link.
•
Benefits: They offer several advantages over physical cards. They are more eco-friendly, easier to share digitally (email, text message), can be more visually engaging, and can even include interactive features like links to your social media profiles or online portfolios.', N'Service', N'NA', '250.00', '250.00', '16.00', N'licencia', 100, 1, N'2026-03-08 07:44:37.0000000', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)

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


-- inventory_movement_approvals: No data to insert


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


-- Data for modules (32 records)
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
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (12, N'Tickets', N'tickets', N'', N'confirmation_number', N'/tickets', 10, 1, NULL, '2025-10-28 02:24:35')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (13, N'Hardware', N'hardware', N'Modulo para gestionar inventario de equipos de cómputo', N'settings', N'/hardware', 11, 1, NULL, '2025-11-11 19:48:15')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (14, N'timeoff', N'timeoff', N'timeoff', N'event_available', N'/time-off/calendar', 0, 1, NULL, '2025-12-06 20:52:19')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (15, N'Tenants', N'tenants', N'Tenants', N'', N'/permissions/Tenants', 0, 1, NULL, '2025-12-28 05:40:08')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (16, N'customers', N'customers', N'customers', N'groups_2', N'customers', 0, 1, NULL, '2026-01-29 05:13:51')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (17, N'products', N'products', N'Module to handle products for proposals', N'inventory_2', N'/products', 15, 1, 16, '2026-02-14 19:00:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (18, N'Timesheet', N'timesheet', N'timesheet', N'schedule', N'/timesheet', 0, 1, NULL, '2026-02-26 03:19:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (19, N'Quotations', N'quotations', N'Module to create quotations to a existing or new customers', N'description', N'/quotations', 19, 1, 16, '2026-03-07 11:32:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (20, N'inventory ', N'inventory', N'Module to handle all Inventory related operations', N'inventory', N'/inventory', 0, 1, NULL, '2026-05-10 17:29:59')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (21, N'Inventory Overview', N'inventory-overview', N'Inventory overview and stock summary', N'inventory_2', N'/inventory', 1, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (22, N'Inventory Entries', N'inventory-entries', N'Inventory stock entries', N'add_box', N'/inventory/entries', 2, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (23, N'Inventory Outputs', N'inventory-outputs', N'Inventory stock outputs', N'outbox', N'/inventory/outputs', 3, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (24, N'Inventory Adjustments', N'inventory-adjustments', N'Inventory stock adjustments', N'tune', N'/inventory/adjustments', 4, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (25, N'Inventory Movements', N'inventory-movements', N'Inventory movement history', N'sync_alt', N'/inventory/movements', 5, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (26, N'Inventory Warehouses', N'inventory-warehouses', N'Inventory warehouse management', N'warehouse', N'/inventory/warehouses', 6, 1, 20, '2026-06-16 03:55:49')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (27, N'workforce-management', N'workforce-management', N'', N'groups', N'', 0, 1, NULL, '2026-06-17 20:18:24')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (28, N'systems', N'systems', N'', N'dns', N'', 0, 1, NULL, '2026-06-17 20:19:04')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (29, N'business-proposals', N'business-proposals', N'', N'request_quote', N'', 0, 1, NULL, '2026-06-17 20:20:46')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (30, N'IT Overview', N'it_dashboard', N'IT Overview', N'computer', N'/it', 80, 1, NULL, '2026-07-19 18:04:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (31, N'IT Services Catalog', N'it_catalog', N'IT Services Catalog', N'design_services', N'/it/catalog', 81, 1, NULL, '2026-07-19 18:04:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (32, N'IT Licenses', N'it_licenses', N'IT Licenses', N'key', N'/it/licenses', 82, 1, NULL, '2026-07-19 18:04:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (33, N'IT Quotations', N'it_quotations', N'IT Quotations', N'request_quote', N'/it/quotations', 83, 1, NULL, '2026-07-19 18:04:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (34, N'IT PDF Templates', N'it_templates', N'IT PDF Templates', N'picture_as_pdf', N'/it/templates', 84, 1, NULL, '2026-07-19 18:04:55')
INSERT [dbo].[modules] ([module_id], [module_name], [module_key], [description], [icon], [route_url], [display_order], [is_active], [parent_module_id], [created_at]) VALUES (35, N'IT Documents', N'it_documents', N'IT Documents', N'folder', N'/it/documents', 85, 1, NULL, '2026-07-19 18:04:55')

SET IDENTITY_INSERT [dbo].[modules] OFF
GO


-- product_attachments: No data to insert


-- Data for product_catalog (6 records)
SET IDENTITY_INSERT [dbo].[product_catalog] ON
GO

INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (7, N'P-11', N'Webpages & Marketing Digital', NULL, NULL, N'licencia', '0.00', 1, N'Package! For only $1200 to $1800, you''ll receive everything you need to establish a strong online presence for your business. Our package includes:
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
Analytics to track your website''s performance.', '2026-02-25 01:23:14')
INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (8, N'P-13', N'Single QR ', NULL, NULL, N'licencia', '0.00', 1, N'QR multiporpouse Marketing', '2026-03-08 06:26:38')
INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (9, N'P-14', N'2 QR''s', NULL, NULL, N'licencia', '0.00', 1, N'Multiporpouse QR''s Marketing', '2026-03-08 06:29:51')
INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (10, N'P-15', N'3 QR''s', NULL, NULL, N'licencia', '0.00', 1, N'Multiporpuse Marketing', '2026-03-08 06:30:48')
INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (11, N'P-16', N'Landing Page', NULL, NULL, N'licencia', '0.00', 1, N'A single page website, also known as a one-page website, is a type of web business card that consists of only one HTML page. Unlike a traditional website, which has multiple pages and navigation menus, a single page website displays all the essential information on a single scrolling page.
- It is more user-friendly and mobile-friendly, as it eliminates the need for clicking and loading new pages
- It is more focused and concise, as it forces you to prioritize the most vital information and messages
- It is more engaging and interactive, as it can use animations, transitions, and effects to create a seamless and immersive experience for the visitors', '2026-03-08 06:46:01')
INSERT [dbo].[product_catalog] ([id], [code], [name], [family_id], [category_id], [unit], [min_stock], [active], [description], [created_at]) VALUES (12, N'P-17', N'Business cards + Digital QR', NULL, NULL, N'licencia', '0.00', 1, N'A web business card, also known as a digital business card, electronic business card, or virtual business card, is the modern take on the traditional paper business card.
Instead of being printed on physical cardstock, a web business card is a webpage containing your contact information and professional details. Like a website, it can be designed and customized to reflect your personal brand.
Here is a breakdown of how web business cards work:
•
Function: Like a paper card, it displays your name, job title, company affiliation, contact details (phone, email), and potentially a website link.
•
Benefits: They offer several advantages over physical cards. They are more eco-friendly, easier to share digitally (email, text message), can be more visually engaging, and can even include interactive features like links to your social media profiles or online portfolios.', '2026-03-08 07:44:37')

SET IDENTITY_INSERT [dbo].[product_catalog] OFF
GO


-- Data for product_specifications (6 records)
SET IDENTITY_INSERT [dbo].[product_specifications] ON
GO

INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (1, 7, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (2, 8, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (3, 9, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (4, 10, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (5, 11, NULL, NULL, NULL, NULL, NULL, NULL)
INSERT [dbo].[product_specifications] ([id], [product_id], [specification], [size], [material], [manufacturer], [model], [notes]) VALUES (6, 12, NULL, NULL, NULL, NULL, NULL, NULL)

SET IDENTITY_INSERT [dbo].[product_specifications] OFF
GO


-- Data for quotations (2 records)
SET IDENTITY_INSERT [dbo].[quotations] ON
GO

INSERT [dbo].[quotations] ([id], [customer_id], [quote_date], [expiration_date], [subtotal], [tax], [discount], [total], [status], [notes], [created_at]) VALUES (1, 3, N'2026-03-22 00:30:55.9300000', N'2026-04-21 00:30:55.9300000', '12.00', '0.00', '0.00', '12.00', N'Draft', N'Quotation for Andy', N'2026-03-22 00:34:15.0262100')
INSERT [dbo].[quotations] ([id], [customer_id], [quote_date], [expiration_date], [subtotal], [tax], [discount], [total], [status], [notes], [created_at]) VALUES (2, 3, N'2026-04-12 17:36:32.5390000', N'2026-05-12 17:36:32.5390000', '5.00', '0.00', '0.00', '5.00', N'Draft', N'quotation test', N'2026-04-12 17:54:48.9380990')

SET IDENTITY_INSERT [dbo].[quotations] OFF
GO


-- quotation_items: No data to insert


-- Data for role_modules (87 records)
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
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 21, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 22, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 23, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 24, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 25, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 26, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 30, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 31, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 32, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 33, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 34, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (1, 35, 1, 1, 1, 1, 1, 1, 1, NULL)
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (2, 3, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (2, 14, 1, 1, 1, 1, 1, 1, 0, '2025-12-22 17:03:13')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 1, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 3, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 5, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 7, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 8, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 10, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 11, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 12, 1, 1, 1, 1, 1, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 13, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 14, 1, 1, 1, 1, 1, 1, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 15, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 17, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 18, 1, 1, 1, 1, 1, 1, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 19, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 21, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 22, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 23, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 24, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 25, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 26, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:36')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 27, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 28, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (3, 29, 0, 0, 0, 0, 0, 0, 0, '2026-06-18 21:51:35')
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
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 1, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:25')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 3, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:25')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 5, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:26')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 7, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:26')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 8, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:27')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 10, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:27')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 11, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:26')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 12, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:28')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 13, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:28')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 14, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:24')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 15, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:24')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 17, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:28')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 18, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:25')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 19, 0, 0, 0, 0, 0, 0, 0, '2026-06-16 03:32:29')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 20, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:32:29')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 21, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 22, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 23, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 24, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 25, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
INSERT [dbo].[role_modules] ([role_id], [module_id], [can_view], [can_create], [can_edit], [can_delete], [can_export], [admin_actions], [other_actions], [assigned_at]) VALUES (9, 26, 1, 1, 1, 1, 1, 1, 1, '2026-06-16 03:55:49')
GO


-- Data for tenant_employees (7 records)
SET IDENTITY_INSERT [dbo].[tenant_employees] ON
GO

INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (2, 1, '2026-01-25 19:15:18', N'jcarlos.villa.rivera@gmail.com', N'$2b$12$mTN9m0Ag46KzBXTCrVugRe4cB800aG2E.v9eA4q3jqIu7c5ERQCcK')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (4, 1, '2026-02-12 01:48:20', N'info@devromo.com', N'$2b$12$gi3XmKKpzRR9ykeM4hRMXOapq3xlqHKI1ruFgrU7/EepRcG72Zrs6')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (5, 1, '2026-03-05 04:00:10', N'javiermendozar73@gmail.com', N'$2b$12$5BBcHMjwPW4SygLgge2Z6uY8eHthHOuigMPf7X8CQV3xGrCD1UQQ2')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (6, 1, '2026-03-12 23:51:03', N'jony.romo001@gmail.com', N'$2b$12$gh.4WetbR5Y6zq8FLY82H.LzIO2yi3JTTIvy6OD5QTUJEf92KxQAG')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (7, NULL, '2026-06-04 16:38:14', N'mordaz@primefire.us', N'$2b$12$/Til07oiYpI0gvC.BcUMouu9qg3/nhQHqgcDw.RyHVvbUsrW1RNDG')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (8, 1, '2026-06-07 04:58:08', N'mordaz@devromo.com', N'$2b$12$ePWR0datxEHIJBVIMQpA5elEQ02aZ9jig4zQ3OD92IFPWW1MsGrZ2')
INSERT [dbo].[tenant_employees] ([id], [tenant_id], [created_at], [email], [password_hash]) VALUES (9, NULL, '2026-06-22 15:05:53', N'axromo@romolifesafety.com', N'$2b$12$8ZoZCQ8uZ8uQbT7JkBWu0.TDe.2sSQe5XeDAXA7Z6uMj9qMQlD0YS')

SET IDENTITY_INSERT [dbo].[tenant_employees] OFF
GO


-- Data for tenant_logos (4 records)
SET IDENTITY_INSERT [dbo].[tenant_logos] ON
GO

INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email], [auth_provider]) VALUES (1, 1, N'Developer''s Romo', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', NULL, N'app.devromo.com', N'assets/fav/devromo.webp', NULL, N'password')
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email], [auth_provider]) VALUES (2, 1, N'Developer''s Romo Local', NULL, N'assets/devromo_logo.webp', N'assets/devromo_bg.webp', N'', N'', NULL, '2026-01-13 04:19:36', '2026-01-25 19:41:43', N'localhost:4201', N'assets/fav/devromo.webp', NULL, N'password')
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email], [auth_provider]) VALUES (3, 2, N'PrimeFire', NULL, N'assets/PrimeFire-Logo.webp', N'assets/prime-fire-hero.webp', N'', N'', NULL, '2026-06-10 21:50:15', '2026-06-11 05:36:57', N'app.primefire.us', N'assets/fav/favicon.png', NULL, N'microsoft')
INSERT [dbo].[tenant_logos] ([logo_id], [tenant_id], [title], [description], [path], [path_background], [primary_color], [secondary_color], [tertiary_color], [created_at], [updated_at], [url], [fav_icon], [email], [auth_provider]) VALUES (4, 2, N'PrimeFire Local', NULL, N'assets/PrimeFire-Logo.webp', N'assets/prime-fire-hero.webp', N'', N'', NULL, '2026-06-10 21:50:23', '2026-06-11 05:37:02', N'localhost:4200', N'assets/fav/favicon.png', NULL, N'microsoft')

SET IDENTITY_INSERT [dbo].[tenant_logos] OFF
GO


-- Data for tickets (15 records)
SET IDENTITY_INSERT [dbo].[tickets] ON
GO

INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (1, N'Outlook Faailure', N'Outlook no funcionan Correectamente ', N'closed', N'normal', N'1h', 2, 2, N'2026-06-04 16:44:45.0000000', N'2026-06-04 16:44:53.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (2, N'Certificados SSL ', N'cambiar los certificados SSL de las siguientes paginas: RLS, SGW, Havana NRG, LicensedMassagePros, PrimeFire', N'closed', N'high', N'4h', 2, 200, N'2026-06-07 05:49:26.0000000', N'2026-06-15 16:57:38.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (3, N'Calendar Excel ', N'Ajustar el Excel Vacations para los empleados RomoLifeSafety', N'closed', N'normal', N'8h', 2, 200, N'2026-06-07 05:52:43.0000000', N'2026-06-15 16:58:06.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (4, N'Agregar Hardware & Software a Inventario & Cambiar a Dominio Devromo', N'Agregar Software & hardware a Inventario app.devromo', N'closed', N'normal', N'4h', 2, 200, N'2026-06-07 05:55:50.0000000', N'2026-06-23 23:20:40.0000000', N'improvement', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (5, N'Agregar Eventos Havana NRG ', N'Cada 1 de cada Mes agregar los eventos de Havana NRG ', N'closed', N'normal', N'1h', 2, 200, N'2026-06-07 05:57:12.0000000', N'2026-07-03 00:14:35.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (6, N'Agregar a Inventario cada 1 de las Maquinas RLS ', N'Agregar al inventario cada uno de los dispositivos de RLS y asegurar que tengan la licencia Microsoft Windows Pro; también meterlos a dominio. ', N'on_hold', N'normal', N'1h', 2, 200, N'2026-06-07 06:01:25.0000000', N'2026-06-23 23:23:51.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (7, N'habilitar usuarios de RLS a la aplicacion ', N'Habilitar a: 
Alex Romo,
Andres Romo,
Ariana Gomez,
Jose Nieto,
Matias Morales,
Mireya Gomez,
Monica Cruz, 
Roberto Romo, todos con el role de Excepto Mireya, Andy y Roberto como Managers', N'on_hold', N'medium', N'8h', 2, 200, N'2026-06-07 06:13:50.0000000', N'2026-06-23 23:23:27.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (8, N'Homologar Iconos con PrimeFire', N'Homologar los iconos de la app Primefire', N'closed', N'low', N'1h', 2, 200, N'2026-06-07 06:16:29.0000000', N'2026-06-17 20:15:33.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (10, N'Instalar OneDrive en Cada una de las máquinas de RLS', N'Asegurarse que RLS ya tiene Onedrive', N'todo', N'high', N'12h', 2, 200, N'2026-06-27 20:41:14.0000000', N'2026-06-27 20:41:14.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (11, N'Revisar cómo Migrar de Cpanel a M365 los correos de Exchange', N'hay un correo de Cpanel que pesa 150 gb aproximadamente, y exchange te da 50 gb la primera version, entonces ver cual version puede cubrir esta necesidad o investigar como particionar el pst', N'todo', N'high', N'12h', 2, 200, N'2026-06-27 20:44:21.0000000', N'2026-06-27 20:44:21.0000000', N'improvement', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (12, N'Arreglar outlook Roberto ', N'Arreglar Outlook de Roberto en ambas máquinas ', N'closed', N'normal', N'1h', 2, 2, N'2026-06-30 01:14:49.0000000', N'2026-06-30 01:18:13.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (13, N'IT Solutions Module', N'Orden de implementación
Fase 1 — Base de datos
Crear esquema it.
Crear categorías.
Crear catálogo.
Crear detalles de servicios y licencias.
Crear quotations e items.
Crear terms y payment schedule.
Crear templates y documents.
Crear índices y constraints.
Fase 2 — FastAPI
Crear paquetes models/it.
Crear schemas/it.
Importar modelos antes de SQLModel.metadata.create_all.
Crear API de categorías.
Crear API de catálogo.
Crear calculadora de cotizaciones.
Crear CRUD de quotations.
Crear generación de números.
Crear PDF.
Crear envío por correo.
Fase 3 — Angular
Crear módulo raíz modules/it.
Crear rutas lazy.
Crear menú.
Crear catálogo.
Crear lista de quotations.
Crear editor de quotation.
Crear resumen único/recurrente.
Crear términos y payment schedule.
Crear preview PDF.
Agregar permisos.
Fase 4 — Seguridad y pruebas
Permisos Angular.
Permisos FastAPI.
Filtrado por tenant_id.
Tests de cálculos.
Tests de PDF.
Validación de estados.
Validación de porcentajes de pago.


En base de datos:

dbo.*   ? infraestructura compartida actual
it.*    ? información exclusiva del módulo IT

En API:
/it/*

En Angular:
src/app/modules/it

El módulo IT no consultaría:
dbo.products
dbo.inventory_movements
dbo.quotations

Solo reutilizaría infraestructura neutral:

dbo.customers
dbo.customer_contacts
dbo.employees
dbo.tenants
dbo.roles / permissions

La cotización que compartiste muestra que el módulo debe manejar costos únicos y anuales, alcance con listas de funcionalidades, hosting, dominio y SSL, tiempos de entrega, impuestos, vigencia y calendario de pagos.

1. Diseño funcional del módulo IT
Menú principal
IT Solutions
+-- Overview
+-- Services Catalog
+-- Licenses
+-- Quotations
+-- PDF Templates
+-- Documents



', N'todo', N'high', N'2w', 2, 1, N'2026-07-16 17:23:56.0000000', N'2026-07-16 21:10:19.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (14, N'Quotaion IT BD', N'15. Resumen de tablas
Tabla	Responsabilidad
it.categories	Categorías IT
it.catalog_items	Servicios, licencias, hosting, dominios, SSL
it.service_details	Detalles exclusivos de servicios
it.license_details	Detalles exclusivos de licencias
it.pdf_templates	Configuración de plantillas PDF
it.quotations	Cabecera de cotización
it.quotation_items	Partidas
it.quotation_terms	Términos y exclusiones
it.payment_schedule	Calendario de pagos
it.quotation_documents	Versiones PDF
it.quotation_status_history	Auditoría de estados

1-. Crear esquema

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = ''it''
)
BEGIN
    EXEC(''CREATE SCHEMA it AUTHORIZATION dbo'');
END;
GO
------------**********------------

2-.También puedes crear una secuencia para generar números de cotización:

CREATE SEQUENCE it.quotation_sequence
    AS BIGINT
    START WITH 1
    INCREMENT BY 1;
GO

/****************/

3-. El backend podrá generar:
Q-Devromo-2026-000001
Q-Devromo-2026-000002
Q-Devromo-2026-000003

4. Tabla it.categories4
CREATE TABLE it.categories (
    category_id INT IDENTITY PRIMARY KEY,

    tenant_id INT NOT NULL,

    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NULL,

    item_type VARCHAR(30) NULL,
    -- SERVICE, LICENSE, HOSTING, DOMAIN, SSL,
    -- SUBSCRIPTION, SUPPORT, OTHER

    is_active BIT NOT NULL DEFAULT 1,

    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT CK_it_categories_item_type
        CHECK (
            item_type IS NULL OR item_type IN (
                ''SERVICE'',
                ''LICENSE'',
                ''HOSTING'',
                ''DOMAIN'',
                ''SSL'',
                ''SUBSCRIPTION'',
                ''SUPPORT'',
                ''OTHER''
            )
        )
);
GO
/********************/
Ejemplos
Web Development
Software Development
Cloud Services
Microsoft Licenses
Security Licenses
Hosting
Domains
Technical Support
Consulting


', N'todo', N'normal', N'2w', 2, 1, N'2026-07-16 17:38:43.0000000', N'2026-07-16 19:21:41.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (15, N'APIs del módulo IT  Todo debe usar el prefijo:', N'Arquitectura Python
Para distinguirlo claramente, no pongas:
api/it_quotations.py
models/it_quotations.py

mezclado con todo lo demás.

Crea paquetes específicos:
PrimeFireApi/
¦
+-- api/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- router.py
¦   ¦   +-- categories.py
¦   ¦   +-- catalog.py
¦   ¦   +-- licenses.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- models/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- catalog.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- schemas/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- catalog.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- services/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- quote_calculator.py
¦   ¦   +-- quote_number_service.py
¦   ¦   +-- quote_service.py
¦   ¦   +-- pdf_service.py
¦   ¦   +-- email_service.py
¦   ¦   +-- document_storage.py
¦
+-- templates/
¦   +-- it/
¦   ¦   +-- quotation_standard.html
¦   ¦   +-- quotation_standard.css
¦
+-- tests/
    +-- it/
    ¦   +-- test_catalog.py
    ¦   +-- test_quote_calculator.py
    ¦   +-- test_quotations.py
    ¦   +-- test_pdf_service.py

APIs del módulo IT

Todo debe usar el prefijo: /it
GET    /it/catalog/categories
GET    /it/catalog/categories/{category_id}
POST   /it/catalog/categories
PATCH  /it/catalog/categories/{category_id}
DELETE /it/catalog/categories/{category_id}

El DELETE debería marcar is_active = 0, no borrar físicamente.
Catálogo

GET    /it/catalog/items
GET    /it/catalog/items/{catalog_item_id}
POST   /it/catalog/items
PATCH  /it/catalog/items/{catalog_item_id}
DELETE /it/catalog/items/{catalog_item_id}

Filtros:
GET /it/catalog/items?item_type=SERVICE
GET /it/catalog/items?item_type=LICENSE
GET /it/catalog/items?billing_cycle=ANNUAL
GET /it/catalog/items?category_id=5
GET /it/catalog/items?search=hosting


', N'todo', N'normal', N'2w', 2, 1, N'2026-07-16 19:19:56.0000000', N'2026-07-16 19:21:27.0000000', N'request', NULL)
INSERT [dbo].[tickets] ([ticket_id], [title], [description], [status], [priority], [sla], [created_by], [assigned_to], [created_at], [updated_at], [ticket_type], [in_progress_at]) VALUES (16, N'Arquitectura Angular', N'Crea el módulo fuera de business_proposals:

src/app/modules/it/
¦
+-- it.routes.ts
¦
+-- pages/
¦   +-- it-overview/
¦   ¦   +-- it-overview.component.ts
¦   ¦   +-- it-overview.component.html
¦   ¦   +-- it-overview.component.css
¦   ¦
¦   +-- catalog/
¦   ¦   +-- catalog-list/
¦   ¦   +-- catalog-form/
¦   ¦   +-- catalog-detail/
¦   ¦
¦   +-- licenses/
¦   ¦   +-- license-list/
¦   ¦   +-- license-form/
¦   ¦   +-- license-detail/
¦   ¦
¦   +-- quotations/
¦   ¦   +-- quotation-list/
¦   ¦   +-- quotation-editor/
¦   ¦   +-- quotation-detail/
¦   ¦   +-- quotation-history/
¦   ¦
¦   +-- templates/
¦   ¦   +-- template-list/
¦   ¦   +-- template-form/
¦   ¦
¦   +-- documents/
¦       +-- document-list/
¦
+-- components/
¦   +-- quotation-header/
¦   +-- quotation-items-table/
¦   +-- quotation-item-dialog/
¦   +-- quotation-summary/
¦   +-- quotation-terms-form/
¦   +-- payment-schedule-editor/
¦   +-- pdf-preview/
¦   +-- status-chip/
¦   +-- recurring-cost-summary/
¦
+-- models/
¦   +-- it-catalog.model.ts
¦   +-- it-license.model.ts
¦   +-- it-quotation.model.ts
¦   +-- it-document.model.ts
¦   +-- it-template.model.ts
¦
+-- services/
    +-- it-catalog.service.ts
    +-- it-license.service.ts
    +-- it-quotation.service.ts
    +-- it-document.service.ts
    +-- it-template.service.ts', N'todo', N'normal', N'2w', 2, 1, N'2026-07-16 21:20:30.0000000', N'2026-07-16 21:20:30.0000000', N'request', NULL)

SET IDENTITY_INSERT [dbo].[tickets] OFF
GO


-- Data for ticket_messages (34 records)
SET IDENTITY_INSERT [dbo].[ticket_messages] ON
GO

INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (1, 7, 2, N'pendiente antes tener meeting con RLS', '2026-06-23 23:22:38', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (2, 13, 2, N'Diseño visual de IT Quotations

IT Quotation Q-IT-2026-0012                    Draft

Customer         Quote Date       Valid Until      Currency
Speedy Welding   07/16/2026       08/15/2026       USD

[ Items ] [ Scope ] [ Terms ] [ Payment Schedule ] [ Notes ] [ History ]

Quote Items
-----------------------------------------------------------------
Description          Type       Billing     Qty    Price    Total
Website Development  Service    One-time     1     450      450
SEO Setup             Service    One-time     1     150      150
Managed Hosting       Hosting    Annual       1     150      150
Domain Registration   Domain     Annual       1      50       50
SSL Certificate       Security   Annual       1      80       80
-----------------------------------------------------------------

One-time subtotal:          $600
Monthly recurring:            $0
Annual recurring:           $280
Tax:                          $0
Initial amount:             $880

[Preview PDF] [Save Draft] [Send to Customer]

El panel de resumen debe separar:

One-time costs
Monthly recurring costs
Annual recurring costs
Initial amount due', '2026-07-16 17:25:29', '2026-07-16 17:26:33', '2026-07-16 17:26:33')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (3, 14, 2, N'5. Tabla it.catalog_items

Esta sustituye a products dentro del módulo IT.

No la llamaría it.products, porque incluye servicios, licencias y suscripciones.

CREATE TABLE it.catalog_items (
    catalog_item_id INT IDENTITY PRIMARY KEY,

    tenant_id INT NOT NULL,
    category_id INT NULL,

    item_type VARCHAR(30) NOT NULL,

    code NVARCHAR(100) NULL,
    sku NVARCHAR(100) NULL,

    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(2000) NULL,

    unit NVARCHAR(50) NOT NULL DEFAULT ''EA'',
    -- EA, HOUR, PROJECT, USER, LICENSE, MONTH, YEAR

    billing_cycle VARCHAR(20) NOT NULL DEFAULT ''ONE_TIME'',
    -- ONE_TIME, MONTHLY, QUARTERLY, ANNUAL

    currency CHAR(3) NOT NULL DEFAULT ''USD'',

    unit_price DECIMAL(18,2) NOT NULL DEFAULT 0,
    cost DECIMAL(18,2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,

    scope_template NVARCHAR(MAX) NULL,

    is_active BIT NOT NULL DEFAULT 1,

    created_by INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    CONSTRAINT FK_it_catalog_items_category
        FOREIGN KEY (category_id)
        REFERENCES it.categories(category_id),

    CONSTRAINT FK_it_catalog_items_employee
        FOREIGN KEY (created_by)
        REFERENCES dbo.employees(employee_id),

    CONSTRAINT CK_it_catalog_items_type
        CHECK (
            item_type IN (
                ''SERVICE'',
                ''LICENSE'',
                ''HOSTING'',
                ''DOMAIN'',
                ''SSL'',
                ''SUBSCRIPTION'',
                ''SUPPORT'',
                ''OTHER''
            )
        ),

    CONSTRAINT CK_it_catalog_items_billing_cycle
        CHECK (
            billing_cycle IN (
                ''ONE_TIME'',
                ''MONTHLY'',
                ''QUARTERLY'',
                ''ANNUAL''
            )
        ),

    CONSTRAINT CK_it_catalog_items_prices
        CHECK (
            unit_price >= 0
            AND cost >= 0
            AND tax_rate >= 0
        )
);
GO', '2026-07-16 17:40:07', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (4, 14, 2, N'CREATE UNIQUE INDEX UX_it_catalog_items_tenant_code
ON it.catalog_items (tenant_id, code)
WHERE code IS NOT NULL;
GO,

ejemplos
Website Development
Mobile App Development
API Integration
SEO Setup
Managed Hosting
Domain Registration
SSL Certificate
Microsoft 365 Business Premium
Adobe Creative Cloud
Monthly Technical Support', '2026-07-16 17:40:42', '2026-07-16 17:44:16', '2026-07-16 17:44:16')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (5, 14, 2, N'6. Tabla it.service_details
Contiene información exclusiva de servicios.

Ejemplo para Website Development:
Deliverables:
- Responsive website
- Contact form
- Google Analytics
- Social media links
- SEO setup

Exclusions:
- Logo creation
- Premium stock images
- Custom third-party integrations


CREATE TABLE it.service_details (
    catalog_item_id INT PRIMARY KEY,

    estimated_delivery_days INT NULL,
    included_hours DECIMAL(10,2) NULL,

    deliverables NVARCHAR(MAX) NULL,
    exclusions NVARCHAR(MAX) NULL,
    technical_requirements NVARCHAR(MAX) NULL,

    CONSTRAINT FK_it_service_details_catalog
        FOREIGN KEY (catalog_item_id)
        REFERENCES it.catalog_items(catalog_item_id),

    CONSTRAINT CK_it_service_delivery_days
        CHECK (
            estimated_delivery_days IS NULL
            OR estimated_delivery_days >= 0
        )
);
GO', '2026-07-16 17:45:05', '2026-07-16 17:45:37', '2026-07-16 17:45:37')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (6, 14, 2, N'7. Tabla it.license_details
Información exclusiva de licencias.

CREATE TABLE it.license_details (
    catalog_item_id INT PRIMARY KEY,

    vendor NVARCHAR(150) NULL,
    vendor_product_code NVARCHAR(100) NULL,

    license_type VARCHAR(30) NULL,
    -- PER_USER, PER_DEVICE, SITE, SUBSCRIPTION

    default_seats INT NULL,
    term_months INT NULL,

    auto_renew BIT NOT NULL DEFAULT 0,

    procurement_notes NVARCHAR(1000) NULL,

    CONSTRAINT FK_it_license_details_catalog
        FOREIGN KEY (catalog_item_id)
        REFERENCES it.catalog_items(catalog_item_id),

    CONSTRAINT CK_it_license_type
        CHECK (
            license_type IS NULL OR license_type IN (
                ''PER_USER'',
                ''PER_DEVICE'',
                ''SITE'',
                ''SUBSCRIPTION''
            )
        ),

    CONSTRAINT CK_it_license_seats
        CHECK (
            default_seats IS NULL
            OR default_seats >= 0
        ),

    CONSTRAINT CK_it_license_term
        CHECK (
            term_months IS NULL
            OR term_months > 0
        )
);
GO', '2026-07-16 17:46:16', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (7, 14, 2, N'8. Tabla it.pdf_templates
Las plantillas pertenecen exclusivamente al módulo IT.
CREATE TABLE it.pdf_templates (
    template_id INT IDENTITY PRIMARY KEY,

    tenant_id INT NOT NULL,

    name NVARCHAR(150) NOT NULL,
    template_key NVARCHAR(100) NOT NULL,

    company_name NVARCHAR(200) NOT NULL,
    logo_url NVARCHAR(500) NULL,

    primary_color NVARCHAR(20) NULL,
    secondary_color NVARCHAR(20) NULL,

    address_text NVARCHAR(500) NULL,
    phone NVARCHAR(50) NULL,
    email NVARCHAR(150) NULL,
    website NVARCHAR(200) NULL,

    default_footer NVARCHAR(1000) NULL,

    signature_name NVARCHAR(150) NULL,
    signature_title NVARCHAR(150) NULL,
    signature_image_url NVARCHAR(500) NULL,

    is_default BIT NOT NULL DEFAULT 0,
    is_active BIT NOT NULL DEFAULT 1,

    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

El template_key apunta a un archivo Jinja:
templates/it/quotation_standard.html
templates/it/quotation_minimal.html
templates/it/quotation_devromo.html', '2026-07-16 17:46:41', '2026-07-16 19:06:22', '2026-07-16 19:06:22')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (8, 14, 2, N'9. Tabla it.quotations

Cabecera de la cotización.

CREATE TABLE it.quotations (
    quotation_id INT IDENTITY PRIMARY KEY,

    tenant_id INT NOT NULL,

    customer_id INT NOT NULL,
    contact_id INT NULL,

    quotation_number NVARCHAR(50) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT ''DRAFT'',

    quote_date DATE NOT NULL,
    expiration_date DATE NOT NULL,

    currency CHAR(3) NOT NULL DEFAULT ''USD'',

    customer_name_snapshot NVARCHAR(200) NOT NULL,
    contact_name_snapshot NVARCHAR(200) NULL,
    customer_email_snapshot NVARCHAR(200) NULL,
    customer_address_snapshot NVARCHAR(1000) NULL,

    one_time_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
    monthly_recurring_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
    annual_recurring_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,

    discount_total DECIMAL(18,2) NOT NULL DEFAULT 0,
    tax_total DECIMAL(18,2) NOT NULL DEFAULT 0,
    initial_total DECIMAL(18,2) NOT NULL DEFAULT 0,

    visible_notes NVARCHAR(MAX) NULL,
    internal_notes NVARCHAR(MAX) NULL,

    template_id INT NULL,

    owner_employee_id INT NULL,
    created_by INT NULL,

    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NULL,

    sent_at DATETIME2 NULL,
    accepted_at DATETIME2 NULL,
    rejected_at DATETIME2 NULL,

    row_version ROWVERSION,

    CONSTRAINT FK_it_quotations_template
        FOREIGN KEY (template_id)
        REFERENCES it.pdf_templates(template_id),

    CONSTRAINT FK_it_quotations_owner
        FOREIGN KEY (owner_employee_id)
        REFERENCES dbo.employees(employee_id),

    CONSTRAINT FK_it_quotations_created_by
        FOREIGN KEY (created_by)
        REFERENCES dbo.employees(employee_id),

    CONSTRAINT CK_it_quotations_status
        CHECK (
            status IN (
                ''DRAFT'',
                ''SENT'',
                ''VIEWED'',
                ''ACCEPTED'',
                ''REJECTED'',
                ''EXPIRED'',
                ''CANCELLED''
            )
        ),

    CONSTRAINT CK_it_quotations_totals
        CHECK (
            one_time_subtotal >= 0
            AND monthly_recurring_subtotal >= 0
            AND annual_recurring_subtotal >= 0
            AND discount_total >= 0
            AND tax_total >= 0
            AND initial_total >= 0
        )
);
GO, 

CREATE UNIQUE INDEX UX_it_quotations_tenant_number
ON it.quotations (tenant_id, quotation_number);
GO', '2026-07-16 19:06:51', '2026-07-16 19:09:47', '2026-07-16 19:09:47')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (9, 14, 2, N'10. Tabla it.quotation_items

Partidas de la cotización.

Notas: 

Aunque el item provenga del catálogo, debes guardar:

name_snapshot
description_snapshot
scope_snapshot
unit_price
tax_rate

Así una cotización antigua no cambia cuando actualices el catálogo

CREATE TABLE it.quotation_items (
    quotation_item_id INT IDENTITY PRIMARY KEY,

    quotation_id INT NOT NULL,
    catalog_item_id INT NULL,

    item_type VARCHAR(30) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL,

    code_snapshot NVARCHAR(100) NULL,
    name_snapshot NVARCHAR(200) NOT NULL,
    description_snapshot NVARCHAR(2000) NULL,
    scope_snapshot NVARCHAR(MAX) NULL,

    quantity DECIMAL(18,2) NOT NULL DEFAULT 1,
    unit NVARCHAR(50) NOT NULL DEFAULT ''EA'',

    unit_price DECIMAL(18,2) NOT NULL DEFAULT 0,
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,

    line_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
    line_discount DECIMAL(18,2) NOT NULL DEFAULT 0,
    line_tax DECIMAL(18,2) NOT NULL DEFAULT 0,
    line_total DECIMAL(18,2) NOT NULL DEFAULT 0,

    term_months INT NULL,
    sort_order INT NOT NULL DEFAULT 0,

    CONSTRAINT FK_it_quotation_items_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES it.quotations(quotation_id),

    CONSTRAINT FK_it_quotation_items_catalog
        FOREIGN KEY (catalog_item_id)
        REFERENCES it.catalog_items(catalog_item_id),

    CONSTRAINT CK_it_quotation_items_quantity
        CHECK (quantity > 0),

    CONSTRAINT CK_it_quotation_items_billing
        CHECK (
            billing_cycle IN (
                ''ONE_TIME'',
                ''MONTHLY'',
                ''QUARTERLY'',
                ''ANNUAL''
            )
        )
);
GO', '2026-07-16 19:10:07', '2026-07-16 19:10:37', '2026-07-16 19:10:37')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (10, 14, 2, N'11. Tabla it.quotation_terms

Condiciones generales del proyecto.

CREATE TABLE it.quotation_terms (
    quotation_id INT PRIMARY KEY,

    delivery_time_text NVARCHAR(500) NULL,
    validity_days INT NULL,

    payment_terms_text NVARCHAR(MAX) NULL,
    exclusions_text NVARCHAR(MAX) NULL,

    tax_note NVARCHAR(MAX) NULL,
    recurring_note NVARCHAR(MAX) NULL,

    warranty_text NVARCHAR(MAX) NULL,
    acceptance_text NVARCHAR(MAX) NULL,

    CONSTRAINT FK_it_quotation_terms_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES it.quotations(quotation_id),

    CONSTRAINT CK_it_quotation_terms_validity
        CHECK (
            validity_days IS NULL
            OR validity_days > 0
        )
);
GO', '2026-07-16 19:11:01', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (11, 14, 2, N'12. Tabla it.payment_schedule

Calendario de pagos.

ejemplos:
1. 50% upon acceptance
2. 25% upon design approval
3. 25% upon final delivery

CREATE TABLE it.payment_schedule (
    payment_schedule_id INT IDENTITY PRIMARY KEY,

    quotation_id INT NOT NULL,

    sequence_number INT NOT NULL,
    description NVARCHAR(250) NOT NULL,

    percentage DECIMAL(5,2) NULL,
    amount DECIMAL(18,2) NULL,

    due_rule NVARCHAR(250) NULL,

    CONSTRAINT FK_it_payment_schedule_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES it.quotations(quotation_id),

    CONSTRAINT CK_it_payment_percentage
        CHECK (
            percentage IS NULL
            OR (
                percentage > 0
                AND percentage <= 100
            )
        ),

    CONSTRAINT CK_it_payment_amount
        CHECK (
            amount IS NULL
            OR amount >= 0
        )
);
GO', '2026-07-16 19:11:26', '2026-07-16 19:12:34', '2026-07-16 19:12:34')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (12, 14, 2, N'13. Tabla it.quotation_documents

Almacena cada versión del PDF generado.

CREATE TABLE it.quotation_documents (
    document_id INT IDENTITY PRIMARY KEY,

    quotation_id INT NOT NULL,

    document_type VARCHAR(30) NOT NULL DEFAULT ''PDF'',

    file_name NVARCHAR(255) NOT NULL,
    storage_path NVARCHAR(1000) NOT NULL,

    document_version INT NOT NULL DEFAULT 1,
    file_hash NVARCHAR(128) NULL,

    generated_by INT NULL,
    generated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_it_documents_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES it.quotations(quotation_id),

    CONSTRAINT FK_it_documents_employee
        FOREIGN KEY (generated_by)
        REFERENCES dbo.employees(employee_id)
);
GO', '2026-07-16 19:12:59', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (13, 14, 2, N'14. Tabla it.quotation_status_history

Auditoría de cambios de estado.

CREATE TABLE it.quotation_status_history (
    history_id INT IDENTITY PRIMARY KEY,

    quotation_id INT NOT NULL,

    previous_status VARCHAR(30) NULL,
    new_status VARCHAR(30) NOT NULL,

    changed_by INT NULL,
    change_notes NVARCHAR(500) NULL,

    changed_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_it_quote_history_quotation
        FOREIGN KEY (quotation_id)
        REFERENCES it.quotations(quotation_id),

    CONSTRAINT FK_it_quote_history_employee
        FOREIGN KEY (changed_by)
        REFERENCES dbo.employees(employee_id)
);
GO', '2026-07-16 19:13:36', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (14, 15, 2, N'Licencias
Puedes utilizar el catálogo con filtro, pero también exponer rutas de conveniencia:

Internamente trabajan con:

it.catalog_items
it.license_details

GET   /it/licenses
GET   /it/licenses/{catalog_item_id}
POST  /it/licenses
PATCH /it/licenses/{catalog_item_id}', '2026-07-16 19:22:34', '2026-07-16 19:22:52', '2026-07-16 19:22:52')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (15, 15, 2, N'Cotizaciones
GET    /it/quotations
GET    /it/quotations/{quotation_id}
POST   /it/quotations
PATCH  /it/quotations/{quotation_id}
DELETE /it/quotations/{quotation_id}', '2026-07-16 19:23:09', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (16, 15, 2, N'Filtros:

GET /it/quotations?status=DRAFT
GET /it/quotations?customer_id=25
GET /it/quotations?date_from=2026-01-01&date_to=2026-12-31
GET /it/quotations?search=Speedy', '2026-07-16 19:23:27', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (17, 15, 2, N'Items
POST   /it/quotations/{quotation_id}/items
PATCH  /it/quotations/{quotation_id}/items/{item_id}
DELETE /it/quotations/{quotation_id}/items/{item_id}
PUT    /it/quotations/{quotation_id}/items/reorder', '2026-07-16 19:23:40', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (18, 15, 2, N'Términos
GET /it/quotations/{quotation_id}/terms
PUT /it/quotations/{quotation_id}/terms', '2026-07-16 19:23:50', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (19, 15, 2, N'Calendario de pagos
GET /it/quotations/{quotation_id}/payment-schedule
PUT /it/quotations/{quotation_id}/payment-schedule', '2026-07-16 19:24:00', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (20, 15, 2, N'PDF y documentos
POST /it/quotations/{quotation_id}/generate-pdf
GET  /it/quotations/{quotation_id}/documents
GET  /it/documents/{document_id}/download', '2026-07-16 19:24:10', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (22, 15, 2, N'Acciones
POST /it/quotations/{quotation_id}/duplicate
POST /it/quotations/{quotation_id}/send
POST /it/quotations/{quotation_id}/change-status
Ejemplo:

{
  "status": "SENT",
  "notes": "Sent to customer by email"
}', '2026-07-16 21:03:47', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (23, 15, 2, N'17. Ejemplo de creación de cotización
{
  "customer_id": 25,
  "contact_id": 10,
  "quote_date": "2026-07-16",
  "expiration_date": "2026-08-15",
  "currency": "USD",
  "template_id": 1,
  "items": [
    {
      "catalog_item_id": 1,
      "quantity": 1,
      "unit_price": 450,
      "billing_cycle": "ONE_TIME",
      "description": "Website development",
      "scope": "- Responsive website\n- Contact form\n- Google Analytics"
    },
    {
      "catalog_item_id": 2,
      "quantity": 1,
      "unit_price": 150,
      "billing_cycle": "ONE_TIME"
    },
    {
      "catalog_item_id": 3,
      "quantity": 1,
      "unit_price": 150,
      "billing_cycle": "ANNUAL",
      "term_months": 12
    },
    {
      "catalog_item_id": 4,
      "quantity": 1,
      "unit_price": 50,
      "billing_cycle": "ANNUAL",
      "term_months": 12
    },
    {
      "catalog_item_id": 5,
      "quantity": 1,
      "unit_price": 80,
      "billing_cycle": "ANNUAL",
      "term_months": 12
    }
  ],
  "terms": {
    "delivery_time_text": "1 to 3 months",
    "validity_days": 30,
    "tax_note": "Prices do not include VAT",
    "recurring_note": "Hosting, domain and SSL renew annually",
    "exclusions_text": "Logo and stock images are not included"
  },
  "payment_schedule": [
    {
      "sequence_number": 1,
      "description": "Upon acceptance",
      "percentage": 50
    },
    {
      "sequence_number": 2,
      "description": "Upon design approval",
      "percentage": 25
    },
    {
      "sequence_number": 3,
      "description": "Upon final delivery",
      "percentage": 25
    }
  ]
}', '2026-07-16 21:03:56', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (24, 13, 2, N'Flujo
IT Catalog
    ?
Create IT Quotation
    ?
Select Customer
    ?
Add Services / Licenses / Hosting / Domain / SSL
    ?
Configure Terms and Payment Schedule
    ?
Calculate one-time and recurring totals
    ?
Generate PDF
    ?
Send to customer
    ?
Draft / Sent / Accepted / Rejected / Expired', '2026-07-16 21:10:39', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (25, 15, 2, N'18. Arquitectura Python

Para distinguirlo claramente, no pongas:

api/it_quotations.py
models/it_quotations.py

mezclado con todo lo demás.

Crea paquetes específicos:

PrimeFireApi/
¦
+-- api/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- router.py
¦   ¦   +-- categories.py
¦   ¦   +-- catalog.py
¦   ¦   +-- licenses.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- models/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- catalog.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- schemas/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- catalog.py
¦   ¦   +-- quotations.py
¦   ¦   +-- documents.py
¦   ¦   +-- templates.py
¦
+-- services/
¦   +-- it/
¦   ¦   +-- __init__.py
¦   ¦   +-- quote_calculator.py
¦   ¦   +-- quote_number_service.py
¦   ¦   +-- quote_service.py
¦   ¦   +-- pdf_service.py
¦   ¦   +-- email_service.py
¦   ¦   +-- document_storage.py
¦
+-- templates/
¦   +-- it/
¦   ¦   +-- quotation_standard.html
¦   ¦   +-- quotation_standard.css
¦
+-- tests/
    +-- it/
    ¦   +-- test_catalog.py
    ¦   +-- test_quote_calculator.py
    ¦   +-- test_quotations.py
    ¦   +-- test_pdf_service.py', '2026-07-16 21:13:07', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (26, 15, 2, N'19. Ejemplo de modelo SQLModel

from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class ITCatalogItems(SQLModel, table=True):
    __tablename__ = "catalog_items"
    __table_args__ = {"schema": "it"}

    catalog_item_id: int | None = Field(
        default=None,
        primary_key=True,
        index=True,
    )

    tenant_id: int
    category_id: int | None = Field(
        default=None,
        foreign_key="it.categories.category_id",
    )

    item_type: str = Field(max_length=30)

    code: str | None = Field(default=None, max_length=100)
    sku: str | None = Field(default=None, max_length=100)

    name: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    unit: str = Field(default="EA", max_length=50)
    billing_cycle: str = Field(default="ONE_TIME", max_length=20)
    currency: str = Field(default="USD", max_length=3)

    unit_price: Decimal = Field(default=Decimal("0"))
    cost: Decimal = Field(default=Decimal("0"))
    tax_rate: Decimal = Field(default=Decimal("0"))

    scope_template: str | None = None

    is_active: bool = True

    created_by: int | None = Field(
        default=None,
        foreign_key="dbo.employees.employee_id",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None,


La diferencia principal es:

__table_args__ = {"schema": "it"}', '2026-07-16 21:14:11', '2026-07-16 21:14:39', '2026-07-16 21:14:39')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (27, 15, 2, N'20. Router agregador

api/it/router.py:

from fastapi import APIRouter

from api.it import catalog, categories, documents, licenses, quotations, templates

router = APIRouter(prefix="/it")

router.include_router(
    categories.router,
    prefix="/catalog/categories",
    tags=["IT Catalog Categories"],
)

router.include_router(
    catalog.router,
    prefix="/catalog/items",
    tags=["IT Catalog"],
)

router.include_router(
    licenses.router,
    prefix="/licenses",
    tags=["IT Licenses"],
)

router.include_router(
    quotations.router,
    prefix="/quotations",
    tags=["IT Quotations"],
)

router.include_router(
    documents.router,
    prefix="/documents",
    tags=["IT Documents"],
)

router.include_router(
    templates.router,
    prefix="/templates",
    tags=["IT PDF Templates"],
)

21. En main.py:

from api.it.router import router as it_router

app.include_router(it_router)

Swagger mostrará grupos claramente separados:

IT Catalog
IT Licenses
IT Quotations
IT Documents
IT PDF Templates', '2026-07-16 21:15:00', '2026-07-16 21:16:50', '2026-07-16 21:16:50')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (29, 15, 2, N'21. Capa de servicios

Los routers no deberían calcular totales directamente.

quote_calculator.py

Responsable de:

line_subtotal
line_discount
line_tax
line_total
one_time_subtotal
monthly_recurring_subtotal
annual_recurring_subtotal
initial_total
quote_number_service.py

Responsable de:

Q-IT-2026-000001
quote_service.py

Responsable de:

crear cotización
actualizar items
guardar snapshots
validar cliente
recalcular totales
cambiar estado
registrar historial
pdf_service.py

Responsable de:

obtener cotización completa
cargar plantilla Jinja2
renderizar HTML
generar PDF
guardar documento
registrar versión
email_service.py

Responsable de:

enviar cotización
adjuntar PDF
registrar fecha de envío
cambiar estado a SENT', '2026-07-16 21:16:10', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (30, 16, 2, N'23. Rutas Angular

it.routes.ts:

import { Routes } from ''@angular/router'';

import { PermissionGuard } from ''../../core/guards/permission.guard'';

export const IT_ROUTES: Routes = [
  {
    path: '''',
    loadComponent: () =>
      import(''./pages/it-overview/it-overview.component'').then(
        (m) => m.ItOverviewComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_dashboard.can_view'' },
  },
  {
    path: ''catalog'',
    loadComponent: () =>
      import(''./pages/catalog/catalog-list/catalog-list.component'').then(
        (m) => m.CatalogListComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_catalog.can_view'' },
  },
  {
    path: ''catalog/create'',
    loadComponent: () =>
      import(''./pages/catalog/catalog-form/catalog-form.component'').then(
        (m) => m.CatalogFormComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_catalog.can_create'' },
  },
  {
    path: ''catalog/:id/edit'',
    loadComponent: () =>
      import(''./pages/catalog/catalog-form/catalog-form.component'').then(
        (m) => m.CatalogFormComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_catalog.can_edit'' },
  },
  {
    path: ''licenses'',
    loadComponent: () =>
      import(''./pages/licenses/license-list/license-list.component'').then(
        (m) => m.LicenseListComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_licenses.can_view'' },
  },
  {
    path: ''quotations'',
    loadComponent: () =>
      import(
        ''./pages/quotations/quotation-list/quotation-list.component''
      ).then((m) => m.QuotationListComponent),
    canActivate: [PermissionGuard],
    data: { permission: ''it_quotations.can_view'' },
  },
  {
    path: ''quotations/create'',
    loadComponent: () =>
      import(
        ''./pages/quotations/quotation-editor/quotation-editor.component''
      ).then((m) => m.QuotationEditorComponent),
    canActivate: [PermissionGuard],
    data: { permission: ''it_quotations.can_create'' },
  },
  {
    path: ''quotations/:id'',
    loadComponent: () =>
      import(
        ''./pages/quotations/quotation-detail/quotation-detail.component''
      ).then((m) => m.QuotationDetailComponent),
    canActivate: [PermissionGuard],
    data: { permission: ''it_quotations.can_view'' },
  },
  {
    path: ''quotations/:id/edit'',
    loadComponent: () =>
      import(
        ''./pages/quotations/quotation-editor/quotation-editor.component''
      ).then((m) => m.QuotationEditorComponent),
    canActivate: [PermissionGuard],
    data: { permission: ''it_quotations.can_edit'' },
  },
  {
    path: ''templates'',
    loadComponent: () =>
      import(''./pages/templates/template-list/template-list.component'').then(
        (m) => m.TemplateListComponent
      ),
    canActivate: [PermissionGuard],
    data: { permission: ''it_templates.can_view'' },
  },
];,', '2026-07-16 21:21:24', '2026-07-16 21:21:56', '2026-07-16 21:21:56')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (31, 16, 2, N'En app.routes.ts:

{
  path: ''it'',
  loadChildren: () =>
    import(''./modules/it/it.routes'').then((m) => m.IT_ROUTES),
  canAEn app.routes.ts:

{
  path: ''it'',
  loadChildren: () =>
    import(''./modules/it/it.routes'').then((m) => m.IT_ROUTES),
  canActivate: [authGuard],
},', '2026-07-16 21:22:02', '2026-07-16 21:22:43', '2026-07-16 21:22:43')
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (32, 16, 2, N'24. Servicios Angular
it-catalog.service.ts
@Injectable({
  providedIn: ''root'',
})
export class ItCatalogService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/it/catalog/items`;

  getAll(params?: ItCatalogFilters): Observable<ItCatalogItem[]> {
    return this.http.get<ItCatalogItem[]>(this.apiUrl, {
      params: { ...params },
    });
  }

  getById(id: number): Observable<ItCatalogItem> {
    return this.http.get<ItCatalogItem>(`${this.apiUrl}/${id}`);
  }

  create(payload: ItCatalogItemCreate): Observable<ItCatalogItem> {
    return this.http.post<ItCatalogItem>(this.apiUrl, payload);
  }

  update(
    id: number,
    payload: Partial<ItCatalogItemCreate>
  ): Observable<ItCatalogItem> {
    return this.http.patch<ItCatalogItem>(
      `${this.apiUrl}/${id}`,
      payload
    );
  }
}', '2026-07-16 21:23:02', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (33, 16, 2, N'it-quotation.service.ts
@Injectable({
  providedIn: ''root'',
})
export class ItQuotationService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/it/quotations`;

  getAll(params?: ItQuotationFilters): Observable<ItQuotationRead[]> {
    return this.http.get<ItQuotationRead[]>(this.apiUrl, {
      params: { ...params },
    });
  }

  getById(id: number): Observable<ItQuotationDetail> {
    return this.http.get<ItQuotationDetail>(`${this.apiUrl}/${id}`);
  }

  create(payload: ItQuotationCreate): Observable<ItQuotationDetail> {
    return this.http.post<ItQuotationDetail>(this.apiUrl, payload);
  }

  update(
    id: number,
    payload: ItQuotationUpdate
  ): Observable<ItQuotationDetail> {
    return this.http.patch<ItQuotationDetail>(
      `${this.apiUrl}/${id}`,
      payload
    );
  }

  generatePdf(id: number): Observable<ItQuotationDocument> {
    return this.http.post<ItQuotationDocument>(
      `${this.apiUrl}/${id}/generate-pdf`,
      {}
    );
  }

  duplicate(id: number): Observable<ItQuotationDetail> {
    return this.http.post<ItQuotationDetail>(
      `${this.apiUrl}/${id}/duplicate`,
      {}
    );
  }

  send(id: number): Observable<ItQuotationDetail> {
    return this.http.post<ItQuotationDetail>(
      `${this.apiUrl}/${id}/send`,
      {}
    );
  }
}', '2026-07-16 21:23:16', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (34, 16, 2, N'25. Menú Angular
<mat-expansion-panel *ngIf="hasAnyItPermission()">
  <mat-expansion-panel-header>
    <mat-panel-title class="nav-title-with-icon">
      <mat-icon>computer</mat-icon>
      IT Solutions
    </mat-panel-title>
  </mat-expansion-panel-header>

  <mat-nav-list>
    <a
      mat-list-item
      routerLink="/it"
      routerLinkActive="active"
      [routerLinkActiveOptions]="{ exact: true }"
      *appHasPermission="''it_dashboard.can_view''"
    >
      Overview
    </a>

    <a
      mat-list-item
      routerLink="/it/catalog"
      routerLinkActive="active"
      *appHasPermission="''it_catalog.can_view''"
    >
      Services Catalog
    </a>

    <a
      mat-list-item
      routerLink="/it/licenses"
      routerLinkActive="active"
      *appHasPermission="''it_licenses.can_view''"
    >
      Licenses
    </a>

    <a
      mat-list-item
      routerLink="/it/quotations"
      routerLinkActive="active"
      *appHasPermission="''it_quotations.can_view''"
    >
      Quotations
    </a>

    <a
      mat-list-item
      routerLink="/it/templates"
      routerLinkActive="active"
      *appHasPermission="''it_templates.can_view''"
    >
      PDF Templates
    </a>
  </mat-nav-list>
</mat-expansion-panel>', '2026-07-16 21:23:32', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (35, 16, 2, N'En app.component.ts:

hasAnyItPermission(): boolean {
  return (
    this.hasPermission(''it_dashboard.can_view'') ||
    this.hasPermission(''it_catalog.can_view'') ||
    this.hasPermission(''it_licenses.can_view'') ||
    this.hasPermission(''it_quotations.can_view'') ||
    this.hasPermission(''it_templates.can_view'')
  );
}', '2026-07-16 21:23:49', NULL, NULL)
INSERT [dbo].[ticket_messages] ([ticket_message_id], [ticket_id], [user_id], [message_txt], [created_at], [updated_at], [edited_at]) VALUES (36, 16, 2, N'26. Permisos

Usa claves sin puntos internos porque tu sistema separa:

moduleKey.permissionType

Módulos:

it_dashboard
it_catalog
it_licenses
it_quotations
it_templates
it_documents

Permisos:

it_dashboard.can_view

it_catalog.can_view
it_catalog.can_create
it_catalog.can_edit
it_catalog.can_delete

it_licenses.can_view
it_licenses.can_create
it_licenses.can_edit
it_licenses.can_delete

it_quotations.can_view
it_quotations.can_create
it_quotations.can_edit
it_quotations.can_delete
it_quotations.can_export
it_quotations.admin_actions

it_templates.can_view
it_templates.can_create
it_templates.can_edit

it_documents.can_view
it_documents.can_export', '2026-07-16 21:24:07', NULL, NULL)

SET IDENTITY_INSERT [dbo].[ticket_messages] OFF
GO


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
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (2, 2, N'vacation', 2026, N'0', N'0', N'6.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (3, 1, N'vacation', 2026, N'0', N'2.00', N'9.00', N'0')
INSERT [dbo].[time_off_balances] ([balance_id], [employee_id], [absence_type], [year], [entitled_days], [used_days], [pending_days], [carryover_days]) VALUES (4, 2, N'sick', 2026, N'0', N'0', N'1.00', N'0')

SET IDENTITY_INSERT [dbo].[time_off_balances] OFF
GO


-- Data for time_off_requests (4 records)
SET IDENTITY_INSERT [dbo].[time_off_requests] ON
GO

INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (18, 2, N'vacation', N'pending', N'full_day', N'2026-03-16', N'2026-03-16', NULL, NULL, NULL, N'1.00', N'holliday day', NULL, NULL, NULL, N'2026-03-13 00:17:12', N'2026-03-13 00:17:12')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (19, 2, N'personal', N'pending', N'full_day', N'2026-03-17', N'2026-03-17', NULL, NULL, NULL, N'1.00', N'i need to go to the doctor', NULL, NULL, NULL, N'2026-03-13 00:17:56', N'2026-03-13 00:17:56')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (20, 2, N'sick', N'pending', N'hours', N'2026-03-18', N'2026-03-18', N'15:00:00', N'23:00:00', N'8.00', N'1.00', N'I''m going to do internally', NULL, NULL, NULL, N'2026-03-13 00:18:49', N'2026-03-13 00:18:49')
INSERT [dbo].[time_off_requests] ([request_id], [employee_id], [absence_type], [status], [time_unit], [start_date], [end_date], [start_time], [end_time], [total_hours], [total_days], [reason], [reviewed_by], [reviewed_at], [review_notes], [created_at], [updated_at]) VALUES (21, 2, N'vacation', N'pending', N'full_day', N'2026-06-29', N'2026-06-29', NULL, NULL, NULL, N'1.00', N'Vacaciones', NULL, NULL, NULL, N'2026-06-24 21:36:32', N'2026-06-24 21:36:32')

SET IDENTITY_INSERT [dbo].[time_off_requests] OFF
GO


-- Data for time_sheet_location_snapshots (35 records)
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
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (15, 200, 4, N'187.209.38.13:58590', N'25.673467640976586', N'-100.47044345055059', N'108', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-16 13:49:52')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (16, 200, 4, N'187.209.38.13:59752', N'25.673480172140415', N'-100.47043421117135', N'120', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-16 23:05:35')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (17, 200, 4, N'187.209.38.13:50180', N'25.673480172140415', N'-100.47043421117135', N'120', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-17 14:04:55')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (18, 200, 4, N'187.209.38.13:53858', N'25.673480172140415', N'-100.47043421117135', N'120', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-17 23:15:14')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (19, 200, 4, N'187.209.38.13:55102', N'25.673479333092423', N'-100.47043487275701', N'114', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-18 14:47:12')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (20, 200, 4, N'189.159.71.86:64714', N'25.6734542225654', N'-100.47044945416258', N'141', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-19 14:49:41')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (21, 200, 4, N'189.159.71.86:64714', N'25.67349271068129', N'-100.4704318653966', N'102', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-19 14:50:27')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (22, 200, 4, N'189.159.71.86:64714', N'25.67349271068129', N'-100.4704318653966', N'102', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-19 14:51:44')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (23, 200, 4, N'189.159.71.86:62921', N'25.67348776823634', N'-100.47043563981804', N'99', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-19 14:56:08')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (24, 200, 4, N'189.159.71.86:65428', N'25.67335973522055', N'-100.47048687183174', N'114', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-19 15:15:39')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (25, 1, 3, N'127.0.0.1', N'25.6411', N'-100.3132', N'10000', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-20 16:59:43')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (26, 1, 3, N'127.0.0.1', N'25.6411', N'-100.3132', N'10000', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-20 16:59:54')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (27, 200, 4, N'189.159.71.86:62983', N'25.67350471855975', N'-100.47042320494873', N'115', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-22 14:54:31')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (28, 200, 4, N'189.159.71.86:62563', N'25.67350471855975', N'-100.47042320494873', N'115', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-23 01:15:45')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (29, 200, 4, N'189.159.71.86:50865', N'25.673479333092423', N'-100.47043487275701', N'114', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-23 15:00:52')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (30, 200, 4, N'189.159.71.86:54511', N'25.673499374427273', N'-100.47042764551898', N'127', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-23 23:15:26')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (31, 200, 4, N'189.159.71.86:62089', N'25.673477506243888', N'-100.47043840830285', N'108', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-24 14:46:49')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (32, 200, 4, N'187.209.54.206:56802', N'25.673404667443588', N'-100.47046576586236', N'103', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-25 14:28:01')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (33, 200, 4, N'187.209.54.206:56802', N'25.673404667443588', N'-100.47046576586236', N'103', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-25 14:28:07')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (34, 200, 4, N'187.209.54.206:56802', N'25.673404667443588', N'-100.47046576586236', N'103', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-25 14:28:22')
INSERT [dbo].[time_sheet_location_snapshots] ([snapshot_id], [employee_id], [customer_id], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [timezone], [location_raw], [captured_at]) VALUES (35, 200, 4, N'187.209.144.164:56014', N'25.67360531307999', N'-100.47037970383478', N'151', NULL, NULL, NULL, N'America/Mexico_City', NULL, N'2026-06-26 22:23:23')

SET IDENTITY_INSERT [dbo].[time_sheet_location_snapshots] OFF
GO


-- Data for time_sheet_punches (25 records)
SET IDENTITY_INSERT [dbo].[time_sheet_punches] ON
GO

INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (1, 2, 4, N'2026-04-27 11:46:15', N'2026-04-27 22:49:17', N'America/Monterrey', NULL, N'25.769180631319543', N'-100.45507778548088', N'19.97672002939698', NULL, NULL, NULL, NULL, 663, N'approved', NULL, 2, N'2026-07-16 16:11:40', N'2026-04-27 11:46:15', N'2026-07-16 16:11:40')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (2, 2, 4, N'2026-04-29 11:50:26', N'2026-04-29 21:50:41', N'America/Monterrey', NULL, N'25.720069771114918', N'-100.52828283346446', N'8.05506678594521', NULL, NULL, NULL, NULL, 600, N'approved', NULL, 2, N'2026-07-16 16:11:45', N'2026-04-29 11:50:26', N'2026-07-16 16:11:45')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (3, 2, 4, N'2026-05-01 17:43:30', N'2026-05-04 17:38:40', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 4315, N'approved', NULL, 2, N'2026-07-16 16:11:53', N'2026-05-01 17:43:30', N'2026-07-16 16:11:53')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (4, 2, 4, N'2026-05-04 17:38:50', N'2026-05-05 13:37:00', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1198, N'approved', NULL, 2, N'2026-07-16 16:12:02', N'2026-05-04 17:38:50', N'2026-07-16 16:12:02')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (5, 2, 4, N'2026-05-05 13:37:33', N'2026-05-06 04:01:51', N'America/Monterrey', NULL, N'25.76918736693643', N'-100.45507510762806', N'11.037352883302603', NULL, NULL, NULL, NULL, 864, N'rejected', NULL, 2, N'2026-06-18 00:40:31', N'2026-05-05 13:37:33', N'2026-06-18 00:40:31')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (6, 2, 4, N'2026-05-11 11:50:52', N'2026-05-12 11:50:51', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1439, N'approved', NULL, 2, N'2026-07-16 16:13:43', N'2026-05-11 11:50:52', N'2026-07-16 16:13:43')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (7, 2, 4, N'2026-05-12 11:50:54', N'2026-05-13 02:00:01', N'America/Monterrey', NULL, N'25.769203606793457', N'-100.4551026175349', N'7.744713461772746', NULL, NULL, NULL, NULL, 849, N'approved', NULL, 2, N'2026-07-16 16:13:53', N'2026-05-12 11:50:54', N'2026-07-16 16:13:53')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (8, 2, 4, N'2026-05-13 11:51:01', N'2026-05-15 14:12:28', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 3021, N'approved', NULL, 2, N'2026-07-16 16:13:35', N'2026-05-13 11:51:01', N'2026-07-16 16:13:35')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (9, 2, 4, N'2026-05-15 14:12:34', N'2026-05-15 14:12:38', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:13:30', N'2026-05-15 14:12:34', N'2026-07-16 16:13:30')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (10, 2, 4, N'2026-05-15 14:12:49', N'2026-05-15 14:12:58', N'America/Monterrey', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:13:25', N'2026-05-15 14:12:49', N'2026-07-16 16:13:25')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (11, 200, 4, N'2026-06-16 13:49:52', N'2026-06-16 23:05:35', N'America/Mexico_City', NULL, N'25.673480172140415', N'-100.47043421117135', N'120', NULL, NULL, NULL, NULL, 555, N'approved', N'16/06/26', 2, N'2026-06-18 00:39:54', N'2026-06-16 13:49:52', N'2026-06-18 00:39:54')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (12, 200, 4, N'2026-06-17 14:04:56', N'2026-06-17 23:15:14', N'America/Mexico_City', NULL, N'25.673480172140415', N'-100.47043421117135', N'120', NULL, NULL, NULL, NULL, 550, N'approved', N'17/06/26', 2, N'2026-06-18 00:39:59', N'2026-06-17 14:04:56', N'2026-06-18 00:39:59')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (13, 200, 4, N'2026-06-18 14:47:14', N'2026-06-19 14:49:32', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1442, N'approved', NULL, 2, N'2026-07-16 16:11:19', N'2026-06-18 14:47:14', N'2026-07-16 16:11:19')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (14, 200, 4, N'2026-06-19 14:49:42', N'2026-06-19 14:49:53', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:12:56', N'2026-06-19 14:49:42', N'2026-07-16 16:12:56')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (15, 200, 4, N'2026-06-19 14:50:29', N'2026-06-19 14:50:48', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:13:08', N'2026-06-19 14:50:29', N'2026-07-16 16:13:08')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (16, 200, 4, N'2026-06-19 14:51:45', N'2026-06-19 14:51:59', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', N'prueba3', 2, N'2026-07-16 16:13:05', N'2026-06-19 14:51:45', N'2026-07-16 16:13:05')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (17, 200, 4, N'2026-06-19 14:56:10', N'2026-06-19 14:56:23', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:13:00', N'2026-06-19 14:56:10', N'2026-07-16 16:13:00')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (18, 200, 4, N'2026-06-19 15:15:40', N'2026-06-19 15:15:53', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', N'prueba4', 2, N'2026-07-16 16:12:50', N'2026-06-19 15:15:40', N'2026-07-16 16:12:50')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (19, 1, 3, N'2026-06-20 16:59:45', N'2026-06-20 16:59:55', N'UTC', NULL, N'25.6411', N'-100.3132', N'10000', NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:12:43', N'2026-06-20 16:59:45', N'2026-07-16 16:12:43')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (20, 200, 4, N'2026-06-22 14:54:32', N'2026-06-23 01:15:45', N'America/Mexico_City', NULL, N'25.67350471855975', N'-100.47042320494873', N'115', NULL, NULL, NULL, NULL, 621, N'approved', N'22/06/2026', 2, N'2026-07-16 16:12:34', N'2026-06-22 14:54:32', N'2026-07-16 16:12:34')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (21, 200, 4, N'2026-06-23 15:00:52', N'2026-06-23 23:15:26', N'America/Mexico_City', NULL, N'25.673499374427273', N'-100.47042764551898', N'127', NULL, NULL, NULL, NULL, 494, N'approved', NULL, 2, N'2026-07-16 16:12:29', N'2026-06-23 15:00:52', N'2026-07-16 16:12:29')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (22, 200, 4, N'2026-06-24 14:46:49', N'2026-06-25 14:28:02', N'America/Mexico_City', NULL, N'25.673404667443588', N'-100.47046576586236', N'103', NULL, NULL, NULL, NULL, 1421, N'approved', NULL, 2, N'2026-07-16 16:12:24', N'2026-06-24 14:46:49', N'2026-07-16 16:12:24')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (23, 200, 4, N'2026-06-25 14:28:08', N'2026-06-25 14:28:17', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:12:21', N'2026-06-25 14:28:08', N'2026-07-16 16:12:21')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (24, 200, 4, N'2026-06-25 14:28:23', N'2026-06-25 14:28:27', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:12:18', N'2026-06-25 14:28:23', N'2026-07-16 16:12:18')
INSERT [dbo].[time_sheet_punches] ([punch_id], [employee_id], [customer_id], [clock_in_at], [clock_out_at], [timezone], [ip_address], [latitude], [longitude], [gps_accuracy], [city], [region], [country], [location_raw], [worked_minutes], [status], [note], [approved_by], [approved_at], [created_at], [updated_at]) VALUES (25, 200, 4, N'2026-06-26 22:23:24', N'2026-06-26 22:23:29', N'America/Mexico_City', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, N'approved', NULL, 2, N'2026-07-16 16:12:15', N'2026-06-26 22:23:24', N'2026-07-16 16:12:15')

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

ALTER TABLE [dbo].[inventory_movement_approvals] WITH CHECK ADD CONSTRAINT [FK_inv_mov_approvals_product]
FOREIGN KEY([product_id])
REFERENCES [dbo].[products] ([id])
GO
ALTER TABLE [dbo].[inventory_movement_approvals] CHECK CONSTRAINT [FK_inv_mov_approvals_product]
GO

ALTER TABLE [dbo].[inventory_movement_approvals] WITH CHECK ADD CONSTRAINT [FK_inv_mov_approvals_warehouse]
FOREIGN KEY([warehouse_id])
REFERENCES [dbo].[warehouses] ([warehouse_id])
GO
ALTER TABLE [dbo].[inventory_movement_approvals] CHECK CONSTRAINT [FK_inv_mov_approvals_warehouse]
GO

ALTER TABLE [dbo].[inventory_movement_approvals] WITH CHECK ADD CONSTRAINT [FK_inv_mov_approvals_movement]
FOREIGN KEY([movement_id])
REFERENCES [dbo].[inventory_movements] ([movement_id])
GO
ALTER TABLE [dbo].[inventory_movement_approvals] CHECK CONSTRAINT [FK_inv_mov_approvals_movement]
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

ALTER TABLE [dbo].[product_attachments] WITH CHECK ADD CONSTRAINT [FK__product_a__produ__269AB60B]
FOREIGN KEY([product_id])
REFERENCES [dbo].[products] ([id])
GO
ALTER TABLE [dbo].[product_attachments] CHECK CONSTRAINT [FK__product_a__produ__269AB60B]
GO

ALTER TABLE [dbo].[product_attachments] WITH CHECK ADD CONSTRAINT [FK__product_a__creat__278EDA44]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[product_attachments] CHECK CONSTRAINT [FK__product_a__creat__278EDA44]
GO

ALTER TABLE [dbo].[product_catalog] WITH CHECK ADD CONSTRAINT [FK__product_c__famil__15702A09]
FOREIGN KEY([family_id])
REFERENCES [dbo].[product_families] ([id])
GO
ALTER TABLE [dbo].[product_catalog] CHECK CONSTRAINT [FK__product_c__famil__15702A09]
GO

ALTER TABLE [dbo].[product_catalog] WITH CHECK ADD CONSTRAINT [FK__product_c__categ__16644E42]
FOREIGN KEY([category_id])
REFERENCES [dbo].[product_categories] ([id])
GO
ALTER TABLE [dbo].[product_catalog] CHECK CONSTRAINT [FK__product_c__categ__16644E42]
GO

ALTER TABLE [dbo].[product_categories] WITH CHECK ADD CONSTRAINT [FK__product_c__famil__0FB750B3]
FOREIGN KEY([family_id])
REFERENCES [dbo].[product_families] ([id])
GO
ALTER TABLE [dbo].[product_categories] CHECK CONSTRAINT [FK__product_c__famil__0FB750B3]
GO

ALTER TABLE [dbo].[product_specifications] WITH CHECK ADD CONSTRAINT [FK__product_s__produ__1940BAED]
FOREIGN KEY([product_id])
REFERENCES [dbo].[product_catalog] ([id])
GO
ALTER TABLE [dbo].[product_specifications] CHECK CONSTRAINT [FK__product_s__produ__1940BAED]
GO

ALTER TABLE [dbo].[products] WITH CHECK ADD CONSTRAINT [FK_products_product_families_family_id]
FOREIGN KEY([family_id])
REFERENCES [dbo].[product_families] ([id])
GO
ALTER TABLE [dbo].[products] CHECK CONSTRAINT [FK_products_product_families_family_id]
GO

ALTER TABLE [dbo].[products] WITH CHECK ADD CONSTRAINT [FK_products_product_categories_category_id]
FOREIGN KEY([category_id])
REFERENCES [dbo].[product_categories] ([id])
GO
ALTER TABLE [dbo].[products] CHECK CONSTRAINT [FK_products_product_categories_category_id]
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

ALTER TABLE [dbo].[quotation_items] WITH CHECK ADD CONSTRAINT [FK_it_quotation_items_quotation]
FOREIGN KEY([quotation_id])
REFERENCES [dbo].[quotations] ([quotation_id])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[quotation_items] CHECK CONSTRAINT [FK_it_quotation_items_quotation]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [fk_quotations_customers]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [fk_quotations_customers]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [FK_it_quotations_customer]
FOREIGN KEY([customer_id])
REFERENCES [dbo].[customers] ([customer_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [FK_it_quotations_customer]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [FK_it_quotations_contact]
FOREIGN KEY([contact_id])
REFERENCES [dbo].[customer_alternate_contacts] ([customer_alternate_contact_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [FK_it_quotations_contact]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [FK_it_quotations_owner]
FOREIGN KEY([owner_employee_id])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [FK_it_quotations_owner]
GO

ALTER TABLE [dbo].[quotations] WITH CHECK ADD CONSTRAINT [FK_it_quotations_created_by]
FOREIGN KEY([created_by])
REFERENCES [dbo].[employees] ([employee_id])
GO
ALTER TABLE [dbo].[quotations] CHECK CONSTRAINT [FK_it_quotations_created_by]
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
-- Total Tables: 43
-- Total Records: 376
-- 
-- Data per table:
--   countries: 5 records
--   addresses: 7 records
--   auth_tokens: 22 records
--   employees: 4 records
--   customers: 5 records
--   customer_alternate_contacts: 1 records
--   roles: 6 records
--   employee_roles: 6 records
--   tenants: 2 records
--   hardware_inventory: 3 records
--   product_families: 4 records
--   product_categories: 4 records
--   products: 6 records
--   warehouses: 1 records
--   inventory_movements: 2 records
--   licenses: 34 records
--   modules: 32 records
--   product_catalog: 6 records
--   product_specifications: 6 records
--   quotations: 2 records
--   role_modules: 87 records
--   tenant_employees: 7 records
--   tenant_logos: 4 records
--   tickets: 15 records
--   ticket_messages: 34 records
--   ticket_recurrence_config: 2 records
--   time_off_balances: 4 records
--   time_off_requests: 4 records
--   time_sheet_location_snapshots: 35 records
--   time_sheet_punches: 25 records
--   time_sheet_settings: 1 records
-- =============================================

PRINT 'Backup restored successfully!'
PRINT 'Total records inserted: 376'
GO
