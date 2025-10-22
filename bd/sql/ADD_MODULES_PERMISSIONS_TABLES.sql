USE [PrimeFireCorp]
GO

/****** Script to add Modules and Permissions system ******/
/****** Execute this script to add the new tables without affecting existing data ******/
/****** Date: 10/19/2025 ******/

-- Check if tables already exist
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Modules')
BEGIN
    PRINT 'Creating Modules table...'
    
    CREATE TABLE [dbo].[Modules](
        [ModuleId] [int] IDENTITY(1,1) NOT NULL,
        [ModuleName] [nvarchar](50) NOT NULL,
        [ModuleKey] [varchar](50) NOT NULL,
        [Description] [nvarchar](200) NULL,
        [Icon] [varchar](50) NULL,
        [RouteUrl] [varchar](100) NULL,
        [DisplayOrder] [int] NULL DEFAULT 0,
        [IsActive] [bit] NOT NULL DEFAULT 1,
        [ParentModuleId] [int] NULL,
        [CreatedAt] [datetime] NOT NULL DEFAULT GETDATE(),
     CONSTRAINT [PK_Modules] PRIMARY KEY CLUSTERED
    (
        [ModuleId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
     CONSTRAINT [UQ_Modules_ModuleKey] UNIQUE NONCLUSTERED
    (
        [ModuleKey] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
    
    PRINT 'Modules table created successfully!'
END
ELSE
BEGIN
    PRINT 'Modules table already exists, skipping...'
END
GO

-- Check if RoleModules table exists
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'RoleModules')
BEGIN
    PRINT 'Creating RoleModules table...'
    
    CREATE TABLE [dbo].[RoleModules](
        [RoleId] [int] NOT NULL,
        [ModuleId] [int] NOT NULL,
        [CanView] [bit] NOT NULL DEFAULT 1,
        [CanCreate] [bit] NOT NULL DEFAULT 0,
        [CanEdit] [bit] NOT NULL DEFAULT 0,
        [CanDelete] [bit] NOT NULL DEFAULT 0,
        [CanExport] [bit] NOT NULL DEFAULT 0,
        [AssignedAt] [datetime] NOT NULL DEFAULT GETDATE(),
     CONSTRAINT [PK_RoleModules] PRIMARY KEY CLUSTERED
    (
        [RoleId] ASC,
        [ModuleId] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
    
    PRINT 'RoleModules table created successfully!'
END
ELSE
BEGIN
    PRINT 'RoleModules table already exists, skipping...'
END
GO

-- Add foreign keys for Modules
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Modules_ParentModule')
BEGIN
    PRINT 'Adding foreign key FK_Modules_ParentModule...'
    ALTER TABLE [dbo].[Modules]  WITH CHECK ADD  CONSTRAINT [FK_Modules_ParentModule] FOREIGN KEY([ParentModuleId])
    REFERENCES [dbo].[Modules] ([ModuleId])
    ALTER TABLE [dbo].[Modules] CHECK CONSTRAINT [FK_Modules_ParentModule]
    PRINT 'Foreign key added!'
END
GO

-- Add foreign keys for RoleModules
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_RoleModules_Roles')
BEGIN
    PRINT 'Adding foreign key FK_RoleModules_Roles...'
    ALTER TABLE [dbo].[RoleModules]  WITH CHECK ADD  CONSTRAINT [FK_RoleModules_Roles] FOREIGN KEY([RoleId])
    REFERENCES [dbo].[Roles] ([RoleId])
    ON DELETE CASCADE
    ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK_RoleModules_Roles]
    PRINT 'Foreign key added!'
END
GO

IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_RoleModules_Modules')
BEGIN
    PRINT 'Adding foreign key FK_RoleModules_Modules...'
    ALTER TABLE [dbo].[RoleModules]  WITH CHECK ADD  CONSTRAINT [FK_RoleModules_Modules] FOREIGN KEY([ModuleId])
    REFERENCES [dbo].[Modules] ([ModuleId])
    ON DELETE CASCADE
    ALTER TABLE [dbo].[RoleModules] CHECK CONSTRAINT [FK_RoleModules_Modules]
    PRINT 'Foreign key added!'
END
GO

-- Insert seed data for Modules
IF NOT EXISTS (SELECT * FROM [dbo].[Modules])
BEGIN
    PRINT 'Inserting seed data for Modules...'
    
    SET IDENTITY_INSERT [dbo].[Modules] ON

    -- Main Modules
    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (1, N'Dashboard', N'dashboard', N'Main dashboard and analytics', N'dashboard', N'/dashboard', 1, 1, NULL)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (2, N'Employees', N'employees', N'Employee management', N'people', N'/employees', 2, 1, NULL)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (3, N'Jobs', N'jobs', N'Job postings management', N'work', N'/jobs', 3, 1, NULL)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (4, N'Curriculums', N'curriculums', N'Curriculum and applications management', N'description', N'/curriculums', 4, 1, NULL)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (5, N'Licenses', N'licenses', N'Software licenses management', N'vpn_key', N'/licenses', 5, 1, NULL)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (6, N'Administration', N'administration', N'System administration', N'settings', N'/administration', 6, 1, NULL)

    -- Sub-modules under Administration
    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (7, N'Roles', N'roles', N'Role management', N'admin_panel_settings', N'/administration/roles', 1, 1, 6)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (8, N'Permissions', N'permissions', N'Module permissions management', N'lock', N'/administration/permissions', 2, 1, 6)

    INSERT [dbo].[Modules] ([ModuleId], [ModuleName], [ModuleKey], [Description], [Icon], [RouteUrl], [DisplayOrder], [IsActive], [ParentModuleId]) 
    VALUES (9, N'Countries', N'countries', N'Countries management', N'public', N'/administration/countries', 3, 1, 6)

    SET IDENTITY_INSERT [dbo].[Modules] OFF
    
    PRINT 'Modules seed data inserted successfully!'
END
ELSE
BEGIN
    PRINT 'Modules already have data, skipping seed data...'
END
GO

-- Insert seed data for RoleModules (Permissions)
IF NOT EXISTS (SELECT * FROM [dbo].[RoleModules])
BEGIN
    PRINT 'Inserting seed data for RoleModules (Permissions)...'
    
    -- Admin Role (RoleId = 1) gets full access to all modules
    INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport]) 
    VALUES 
    (1, 1, 1, 1, 1, 1, 1), 
    (1, 2, 1, 1, 1, 1, 1), 
    (1, 3, 1, 1, 1, 1, 1), 
    (1, 4, 1, 1, 1, 1, 1), 
    (1, 5, 1, 1, 1, 1, 1), 
    (1, 6, 1, 1, 1, 1, 1), 
    (1, 7, 1, 1, 1, 1, 1), 
    (1, 8, 1, 1, 1, 1, 1), 
    (1, 9, 1, 1, 1, 1, 1)

    -- Manager Role (RoleId = 2) gets view and edit access to most modules
    INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport]) 
    VALUES 
    (2, 1, 1, 0, 0, 0, 1), 
    (2, 2, 1, 1, 1, 0, 1), 
    (2, 3, 1, 1, 1, 0, 1), 
    (2, 4, 1, 0, 1, 0, 1), 
    (2, 5, 1, 1, 1, 0, 1)

    -- User Role (RoleId = 3) gets basic view access
    INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport]) 
    VALUES 
    (3, 1, 1, 0, 0, 0, 0), 
    (3, 2, 1, 0, 0, 0, 0), 
    (3, 3, 1, 0, 0, 0, 0)

    -- HR Role (RoleId = 4) gets full access to employees, jobs, and curriculums
    INSERT [dbo].[RoleModules] ([RoleId], [ModuleId], [CanView], [CanCreate], [CanEdit], [CanDelete], [CanExport]) 
    VALUES 
    (4, 1, 1, 0, 0, 0, 1), 
    (4, 2, 1, 1, 1, 1, 1), 
    (4, 3, 1, 1, 1, 1, 1), 
    (4, 4, 1, 1, 1, 1, 1)
    
    PRINT 'RoleModules seed data inserted successfully!'
END
ELSE
BEGIN
    PRINT 'RoleModules already have data, skipping seed data...'
END
GO

PRINT ''
PRINT '=========================================='
PRINT 'MIGRATION COMPLETED SUCCESSFULLY!'
PRINT '=========================================='
PRINT 'Tables created:'
PRINT '  - Modules (9 records)'
PRINT '  - RoleModules (25 permission records)'
PRINT ''
PRINT 'You can now use the permissions API endpoints:'
PRINT '  GET /modules'
PRINT '  GET /permissions'
PRINT '  GET /permissions/role/{role_id}'
PRINT '=========================================='
GO

