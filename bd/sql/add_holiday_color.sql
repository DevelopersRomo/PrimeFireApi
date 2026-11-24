-- Holidays: icon color chosen in the Holidays screen (#rrggbb). NULL = the app picks one from the name.
--
-- Run this ONE file against EVERY database (main + each tenant) BEFORE deploying the API that reads
-- holidays.color: until the column exists, every holiday query fails.
-- Idempotent: safe to run more than once. Only adds a nullable column; no data changes.
-- No GO on purpose: it is a single batch, so it also runs in DBeaver.

IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.holidays')
    AND name = 'color'
)
BEGIN
    ALTER TABLE [dbo].[holidays] ADD [color] VARCHAR(7) NULL;
END;
