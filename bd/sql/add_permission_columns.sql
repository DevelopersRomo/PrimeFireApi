USE [PrimeFireCorp]
GO

/****** Script to add AdminActions and OtherActions columns to RoleModules table ******/
/****** Execute this script to add the new columns without affecting existing data ******/

-- Check if AdminActions column exists
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('RoleModules') AND name = 'AdminActions')
BEGIN
    ALTER TABLE RoleModules ADD AdminActions BIT NOT NULL DEFAULT 0
    PRINT 'AdminActions column added successfully!'
END
ELSE
BEGIN
    PRINT 'AdminActions column already exists, skipping...'
END
GO

-- Check if OtherActions column exists
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('RoleModules') AND name = 'OtherActions')
BEGIN
    ALTER TABLE RoleModules ADD OtherActions BIT NOT NULL DEFAULT 0
    PRINT 'OtherActions column added successfully!'
END
ELSE
BEGIN
    PRINT 'OtherActions column already exists, skipping...'
END
GO

PRINT ''
PRINT '=========================================='
PRINT 'MIGRATION COMPLETED SUCCESSFULLY!'
PRINT '=========================================='
PRINT 'New columns added to RoleModules table:'
PRINT '  - AdminActions (BIT, default 0)'
PRINT '  - OtherActions (BIT, default 0)'
PRINT '=========================================='
GO
