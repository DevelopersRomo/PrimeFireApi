-- Customers module tables creation
-- Generated on: 2026-01-25
-- Creates Customers, Addresses, CustomerNotes, CustomerAlternateContacts, and CustomerAttachments tables

GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- =============================================
-- Table: Addresses (Reusable address table)
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Addresses]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Addresses](
        [AddressId] [int] IDENTITY(1,1) NOT NULL,
        [Address1] [nvarchar](200) NOT NULL,
        [Address2] [nvarchar](200) NULL,
        [City] [nvarchar](100) NOT NULL,
        [State] [nvarchar](100) NOT NULL,
        [ZipCode] [nvarchar](20) NOT NULL,
        [CountryId] [int] NOT NULL,
        [GooglePlaceId] [nvarchar](255) NULL,
        [IsValidated] [bit] NOT NULL CONSTRAINT [DF_Addresses_IsValidated] DEFAULT (0),
        [ValidatedAt] [datetime2](7) NULL,
        [CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_Addresses_CreatedAt] DEFAULT (SYSUTCDATETIME()),
     CONSTRAINT [PK_Addresses] PRIMARY KEY CLUSTERED
    (
        [AddressId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Addresses_Countries')
BEGIN
    ALTER TABLE [dbo].[Addresses] WITH CHECK ADD CONSTRAINT [FK_Addresses_Countries]
        FOREIGN KEY([CountryId]) REFERENCES [dbo].[Countries] ([CountryId])
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Addresses_CountryId' AND object_id = OBJECT_ID(N'[dbo].[Addresses]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Addresses_CountryId] ON [dbo].[Addresses]
    (
        [CountryId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

-- =============================================
-- Table: Customers
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Customers]') AND type in (N'U'))
BEGIN
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
        [CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_Customers_CreatedAt] DEFAULT (SYSUTCDATETIME()),
        [UpdatedAt] [datetime2](7) NULL,
        [CreatedBy] [int] NOT NULL,
     CONSTRAINT [PK_Customers] PRIMARY KEY CLUSTERED
    (
        [CustomerId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_Customers_CustomerType')
BEGIN
    ALTER TABLE [dbo].[Customers] ADD CONSTRAINT [CK_Customers_CustomerType]
        CHECK ([CustomerType] IN ('residential', 'commercial'))
END
GO

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_Customers_Market')
BEGIN
    ALTER TABLE [dbo].[Customers] ADD CONSTRAINT [CK_Customers_Market]
        CHECK ([Market] IS NULL OR [Market] IN ('commercial', 'individual', 'environmental', 'engineering'))
END
GO

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_Customers_DtdPotential')
BEGIN
    ALTER TABLE [dbo].[Customers] ADD CONSTRAINT [CK_Customers_DtdPotential]
        CHECK ([DtdPotential] IS NULL OR [DtdPotential] IN ('very_high', 'high', 'medium', 'low', 'very_low', 'one_off', 'prospect'))
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Customers_PrimaryAddressId_Addresses')
BEGIN
    ALTER TABLE [dbo].[Customers] WITH CHECK ADD CONSTRAINT [FK_Customers_PrimaryAddressId_Addresses]
        FOREIGN KEY([PrimaryAddressId]) REFERENCES [dbo].[Addresses] ([AddressId])
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Customers_CreatedBy_Employees')
BEGIN
    ALTER TABLE [dbo].[Customers] WITH CHECK ADD CONSTRAINT [FK_Customers_CreatedBy_Employees]
        FOREIGN KEY([CreatedBy]) REFERENCES [dbo].[Employees] ([EmployeeId])
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Customers_CustomerType' AND object_id = OBJECT_ID(N'[dbo].[Customers]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Customers_CustomerType] ON [dbo].[Customers]
    (
        [CustomerType] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Customers_PrimaryEmail' AND object_id = OBJECT_ID(N'[dbo].[Customers]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Customers_PrimaryEmail] ON [dbo].[Customers]
    (
        [PrimaryEmail] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Customers_CreatedBy' AND object_id = OBJECT_ID(N'[dbo].[Customers]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Customers_CreatedBy] ON [dbo].[Customers]
    (
        [CreatedBy] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Customers_PrimaryAddressId' AND object_id = OBJECT_ID(N'[dbo].[Customers]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Customers_PrimaryAddressId] ON [dbo].[Customers]
    (
        [PrimaryAddressId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

-- =============================================
-- Table: CustomerNotes
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CustomerNotes]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[CustomerNotes](
        [CustomerNoteId] [int] IDENTITY(1,1) NOT NULL,
        [CustomerId] [int] NOT NULL,
        [NoteText] [nvarchar](MAX) NOT NULL,
        [CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_CustomerNotes_CreatedAt] DEFAULT (SYSUTCDATETIME()),
        [UpdatedAt] [datetime2](7) NULL,
        [CreatedBy] [int] NOT NULL,
     CONSTRAINT [PK_CustomerNotes] PRIMARY KEY CLUSTERED
    (
        [CustomerNoteId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_CustomerNotes_CustomerId_Customers')
BEGIN
    ALTER TABLE [dbo].[CustomerNotes] WITH CHECK ADD CONSTRAINT [FK_CustomerNotes_CustomerId_Customers]
        FOREIGN KEY([CustomerId]) REFERENCES [dbo].[Customers] ([CustomerId]) ON DELETE CASCADE
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_CustomerNotes_CreatedBy_Employees')
BEGIN
    ALTER TABLE [dbo].[CustomerNotes] WITH CHECK ADD CONSTRAINT [FK_CustomerNotes_CreatedBy_Employees]
        FOREIGN KEY([CreatedBy]) REFERENCES [dbo].[Employees] ([EmployeeId])
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_CustomerNotes_CustomerId' AND object_id = OBJECT_ID(N'[dbo].[CustomerNotes]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_CustomerNotes_CustomerId] ON [dbo].[CustomerNotes]
    (
        [CustomerId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

-- =============================================
-- Table: CustomerAlternateContacts
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CustomerAlternateContacts]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[CustomerAlternateContacts](
        [CustomerAlternateContactId] [int] IDENTITY(1,1) NOT NULL,
        [CustomerId] [int] NOT NULL,
        [Name] [nvarchar](200) NOT NULL,
        [Email] [nvarchar](255) NULL,
        [Phone] [nvarchar](20) NULL,
        [CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_CustomerAlternateContacts_CreatedAt] DEFAULT (SYSUTCDATETIME()),
        [UpdatedAt] [datetime2](7) NULL,
     CONSTRAINT [PK_CustomerAlternateContacts] PRIMARY KEY CLUSTERED
    (
        [CustomerAlternateContactId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_CustomerAlternateContacts_CustomerId_Customers')
BEGIN
    ALTER TABLE [dbo].[CustomerAlternateContacts] WITH CHECK ADD CONSTRAINT [FK_CustomerAlternateContacts_CustomerId_Customers]
        FOREIGN KEY([CustomerId]) REFERENCES [dbo].[Customers] ([CustomerId]) ON DELETE CASCADE
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_CustomerAlternateContacts_CustomerId' AND object_id = OBJECT_ID(N'[dbo].[CustomerAlternateContacts]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_CustomerAlternateContacts_CustomerId] ON [dbo].[CustomerAlternateContacts]
    (
        [CustomerId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO

-- =============================================
-- Table: CustomerAttachments
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CustomerAttachments]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[CustomerAttachments](
        [CustomerAttachmentId] [int] IDENTITY(1,1) NOT NULL,
        [CustomerId] [int] NOT NULL,
        [FileName] [nvarchar](255) NOT NULL,
        [FileType] [nvarchar](100) NULL,
        [FilePath] [nvarchar](500) NULL,
        [CreatedAt] [datetime2](7) NOT NULL CONSTRAINT [DF_CustomerAttachments_CreatedAt] DEFAULT (SYSUTCDATETIME()),
        [CreatedBy] [int] NOT NULL,
     CONSTRAINT [PK_CustomerAttachments] PRIMARY KEY CLUSTERED
    (
        [CustomerAttachmentId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_CustomerAttachments_CustomerId_Customers')
BEGIN
    ALTER TABLE [dbo].[CustomerAttachments] WITH CHECK ADD CONSTRAINT [FK_CustomerAttachments_CustomerId_Customers]
        FOREIGN KEY([CustomerId]) REFERENCES [dbo].[Customers] ([CustomerId]) ON DELETE CASCADE
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_CustomerAttachments_CreatedBy_Employees')
BEGIN
    ALTER TABLE [dbo].[CustomerAttachments] WITH CHECK ADD CONSTRAINT [FK_CustomerAttachments_CreatedBy_Employees]
        FOREIGN KEY([CreatedBy]) REFERENCES [dbo].[Employees] ([EmployeeId])
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_CustomerAttachments_CustomerId' AND object_id = OBJECT_ID(N'[dbo].[CustomerAttachments]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_CustomerAttachments_CustomerId] ON [dbo].[CustomerAttachments]
    (
        [CustomerId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
END
GO
