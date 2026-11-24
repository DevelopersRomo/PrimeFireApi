-- devromo only: merge country "Mexico" into "MX" and assign MX to every employee.
-- Run BEFORE seed_official_holidays_2026_2027.sql. Single batch, single transaction.
--   1. Run with @dry_run = 1 -> shows the result, then ROLLS BACK.
--   2. Run with @dry_run = 0 to COMMIT.

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @dry_run bit = 1;  -- 1 = preview + rollback, 0 = commit

DECLARE @keep int = (SELECT country_id FROM dbo.countries WHERE LTRIM(RTRIM(name)) = N'MX');
DECLARE @drop int = (SELECT country_id FROM dbo.countries WHERE LTRIM(RTRIM(name)) COLLATE Latin1_General_CI_AI = N'Mexico');
DECLARE @sql nvarchar(max);

IF @keep IS NULL
    THROW 50002, 'Country "MX" not found. Nothing changed.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    IF @drop IS NOT NULL AND @drop <> @keep
    BEGIN
        -- Repoint every column with a foreign key to dbo.countries (employees, jobs, addresses, holidays...).
        SELECT @sql = STRING_AGG(
            CAST(N'UPDATE ' + QUOTENAME(SCHEMA_NAME(t.schema_id)) + N'.' + QUOTENAME(t.name)
                 + N' SET ' + QUOTENAME(c.name) + N' = @keep WHERE ' + QUOTENAME(c.name) + N' = @drop;' AS nvarchar(max)), N' ')
        FROM sys.foreign_key_columns fkc
        JOIN sys.tables t ON t.object_id = fkc.parent_object_id
        JOIN sys.columns c ON c.object_id = fkc.parent_object_id AND c.column_id = fkc.parent_column_id
        WHERE fkc.referenced_object_id = OBJECT_ID('dbo.countries');

        IF @sql IS NOT NULL
            EXEC sp_executesql @sql, N'@keep int, @drop int', @keep, @drop;

        DELETE FROM dbo.countries WHERE country_id = @drop;
    END

    UPDATE dbo.employees SET country_id = @keep WHERE country_id IS NULL OR country_id <> @keep;

    SELECT country_id, name FROM dbo.countries ORDER BY country_id;
    SELECT COUNT(*) AS total, SUM(CASE WHEN country_id = @keep THEN 1 ELSE 0 END) AS in_mx FROM dbo.employees;

    IF @dry_run = 1
    BEGIN
        ROLLBACK TRANSACTION;
        PRINT 'DRY RUN: everything rolled back. Set @dry_run = 0 to commit.';
    END
    ELSE
    BEGIN
        COMMIT TRANSACTION;
        PRINT 'Committed.';
    END
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
