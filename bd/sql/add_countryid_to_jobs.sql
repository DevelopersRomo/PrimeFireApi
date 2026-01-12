-- Migration script to add CountryId to Jobs table in existing external databases
-- Run this on each external tenant database that was created before this fix

IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Jobs]') 
    AND name = 'CountryId'
)
BEGIN
    ALTER TABLE [dbo].[Jobs] ADD [CountryId] [smallint] NULL;
    PRINT 'Added CountryId column to Jobs table';
END
ELSE
BEGIN
    PRINT 'CountryId column already exists in Jobs table';
END
GO

-- Add foreign key constraint if it doesn't exist
IF NOT EXISTS (
    SELECT * FROM sys.foreign_keys 
    WHERE name = 'FK_Jobs_Country'
)
BEGIN
    ALTER TABLE [dbo].[Jobs] WITH CHECK ADD CONSTRAINT [FK_Jobs_Country] 
    FOREIGN KEY([CountryId]) REFERENCES [dbo].[Countries] ([CountryId]);
    PRINT 'Added FK_Jobs_Country constraint';
END
ELSE
BEGIN
    PRINT 'FK_Jobs_Country constraint already exists';
END
GO

