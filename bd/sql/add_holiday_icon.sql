-- Holidays: icon chosen in the Holidays screen (Material Icons name). NULL = the app picks one from the name.
--
-- Run this ONE file against EVERY database (main + each tenant) BEFORE deploying the API that reads
-- holidays.icon: until the column exists, every holiday query fails.
-- Idempotent: safe to run more than once. Only adds a nullable column; no data changes.

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.holidays')
    AND name = 'icon'
)
BEGIN
    ALTER TABLE [dbo].[holidays] ADD [icon] NVARCHAR(50) NULL;
END;
