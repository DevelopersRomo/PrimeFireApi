USE [PrimeFireCorp]
GO

-- Add CountryId column to Jobs table
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('dbo.Jobs') 
    AND name = 'CountryId'
)
BEGIN
    PRINT 'Adding CountryId column to Jobs table...'
    
    ALTER TABLE [dbo].[Jobs]
    ADD [CountryId] [int] NULL
    
    PRINT 'CountryId column added successfully!'
    
    -- Add foreign key constraint
    IF NOT EXISTS (
        SELECT * FROM sys.foreign_keys 
        WHERE name = 'FK_Jobs_Countries'
    )
    BEGIN
        PRINT 'Adding foreign key FK_Jobs_Countries...'
        
        ALTER TABLE [dbo].[Jobs] 
        WITH CHECK ADD CONSTRAINT [FK_Jobs_Countries] 
        FOREIGN KEY([CountryId])
        REFERENCES [dbo].[Countries] ([CountryId])
        
        ALTER TABLE [dbo].[Jobs] 
        CHECK CONSTRAINT [FK_Jobs_Countries]
        
        PRINT 'Foreign key FK_Jobs_Countries added successfully!'
    END
    ELSE
    BEGIN
        PRINT 'Foreign key FK_Jobs_Countries already exists, skipping...'
    END
END
ELSE
BEGIN
    PRINT 'CountryId column already exists in Jobs table, skipping...'
END
GO

PRINT ''
PRINT '=========================================='
PRINT 'MIGRATION COMPLETED SUCCESSFULLY!'
PRINT '=========================================='
PRINT 'Jobs table now has CountryId column'
PRINT '=========================================='
GO

