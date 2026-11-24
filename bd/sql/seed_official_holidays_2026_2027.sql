-- Official public holidays 2026-2027 for USA, Mexico, Dominican Republic and Puerto Rico.
--
-- Run this ONE file against EVERY database (main DB + each tenant DB), in SSMS / Azure Data Studio.
-- Single batch, single transaction. Idempotent: never updates or deletes rows, only inserts what is missing.
--
--   1. Run with @dry_run = 1  -> shows what would happen, then ROLLS BACK.
--   2. Review the result sets, then run with @dry_run = 0 to COMMIT.
--
-- What it does:
--   a) Resolves each country by name aliases (case/accent insensitive). Creates the country only if none matches.
--      Duplicates (e.g. "MX" and "Mexico"): every matching row that has employees gets the holidays, so each
--      employee sees them; if none has employees, only the lowest country_id is used.
--   b) If the legacy UNIQUE(date) from time_off.sql still exists, replaces it with UNIQUE(date, country_id),
--      which is what the API already enforces (one holiday per date per country). Without this, the
--      same date in two countries (Jan 1, Dec 25, Jul 4...) fails.
--   c) Inserts holidays dated >= @from_date, skipping a date that already has a holiday for that
--      country or a global (country_id NULL) one.
--
-- Sources (dates are the official day off, i.e. already moved/observed):
--   USA: OPM federal holidays (5 U.S.C. 6103), opm.gov/policy-data-oversight/pay-leave/federal-holidays
--   MX : Ley Federal del Trabajo, art. 74 (descanso obligatorio)
--   DO : Ministerio de Trabajo, Ley 139-97 calendars 2026 and 2027 (mt.gob.do)
--   PR : OATRH (Gobierno de Puerto Rico) holiday lists 2026 and 2027

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @dry_run bit = 0;                          -- 1 = preview + rollback, 0 = commit
DECLARE @from_date char(10) = CONVERT(char(10), DATEFROMPARTS(YEAR(GETDATE()), 1, 1), 23);  -- whole current year + later

DECLARE @aliases TABLE (code char(2) NOT NULL, alias nvarchar(50) NOT NULL);
INSERT INTO @aliases (code, alias) VALUES
    ('US', N'USA'), ('US', N'US'), ('US', N'U.S.'), ('US', N'U.S.A.'), ('US', N'United States'),
    ('US', N'United States of America'), ('US', N'America'), ('US', N'Estados Unidos'), ('US', N'EEUU'), ('US', N'EE.UU.'),
    ('MX', N'Mexico'), ('MX', N'MX'), ('MX', N'MEX'), ('MX', N'Estados Unidos Mexicanos'),
    ('DO', N'Dominican Republic'), ('DO', N'Republica Dominicana'), ('DO', N'DO'), ('DO', N'RD'), ('DO', N'DOM'),
    ('PR', N'Puerto Rico'), ('PR', N'PR');

-- Name used only when the country does not exist yet (same spelling as create_external_db.sql).
DECLARE @canonical TABLE (code char(2) NOT NULL PRIMARY KEY, name nvarchar(20) NOT NULL);
INSERT INTO @canonical (code, name) VALUES
    ('US', N'USA'), ('MX', N'Mexico'), ('DO', N'Dominican Republic'), ('PR', N'Puerto Rico');

-- Target rows per country code (more than one only when duplicate rows are in use by employees).
DECLARE @countries TABLE (code char(2) NOT NULL, country_id int NOT NULL, created bit NOT NULL DEFAULT 0, PRIMARY KEY (code, country_id));

DECLARE @holidays TABLE (code char(2) NOT NULL, [date] char(10) NOT NULL, name nvarchar(100) NOT NULL);
INSERT INTO @holidays (code, [date], name) VALUES
    -- USA (OPM, observed dates)
    ('US', '2026-01-01', N'New Year''s Day'),
    ('US', '2026-01-19', N'Birthday of Martin Luther King, Jr.'),
    ('US', '2026-02-16', N'Washington''s Birthday'),
    ('US', '2026-05-25', N'Memorial Day'),
    ('US', '2026-06-19', N'Juneteenth National Independence Day'),
    ('US', '2026-07-03', N'Independence Day (observed)'),
    ('US', '2026-09-07', N'Labor Day'),
    ('US', '2026-10-12', N'Columbus Day'),
    ('US', '2026-11-11', N'Veterans Day'),
    ('US', '2026-11-26', N'Thanksgiving Day'),
    ('US', '2026-12-25', N'Christmas Day'),
    ('US', '2027-01-01', N'New Year''s Day'),
    ('US', '2027-01-18', N'Birthday of Martin Luther King, Jr.'),
    ('US', '2027-02-15', N'Washington''s Birthday'),
    ('US', '2027-05-31', N'Memorial Day'),
    ('US', '2027-06-18', N'Juneteenth National Independence Day (observed)'),
    ('US', '2027-07-05', N'Independence Day (observed)'),
    ('US', '2027-09-06', N'Labor Day'),
    ('US', '2027-10-11', N'Columbus Day'),
    ('US', '2027-11-11', N'Veterans Day'),
    ('US', '2027-11-25', N'Thanksgiving Day'),
    ('US', '2027-12-24', N'Christmas Day (observed)'),
    ('US', '2027-12-31', N'New Year''s Day 2028 (observed)'),
    -- Mexico (LFT art. 74)
    ('MX', '2026-01-01', N'New Year''s Day'),
    ('MX', '2026-02-02', N'Constitution Day'),
    ('MX', '2026-03-16', N'Benito Juarez''s Birthday'),
    ('MX', '2026-05-01', N'Labor Day'),
    ('MX', '2026-09-16', N'Independence Day'),
    ('MX', '2026-11-16', N'Revolution Day'),
    ('MX', '2026-12-25', N'Christmas Day'),
    ('MX', '2027-01-01', N'New Year''s Day'),
    ('MX', '2027-02-01', N'Constitution Day'),
    ('MX', '2027-03-15', N'Benito Juarez''s Birthday'),
    ('MX', '2027-05-01', N'Labor Day'),
    ('MX', '2027-09-16', N'Independence Day'),
    ('MX', '2027-11-15', N'Revolution Day'),
    ('MX', '2027-12-25', N'Christmas Day'),
    -- Dominican Republic (Ministerio de Trabajo, dates already moved by Ley 139-97)
    ('DO', '2026-01-01', N'New Year''s Day'),
    ('DO', '2026-01-05', N'Epiphany (moved from Jan 6)'),
    ('DO', '2026-01-21', N'Our Lady of Altagracia'),
    ('DO', '2026-01-26', N'Duarte Day'),
    ('DO', '2026-02-27', N'Independence Day'),
    ('DO', '2026-04-03', N'Good Friday'),
    ('DO', '2026-05-04', N'Labor Day (moved from May 1)'),
    ('DO', '2026-06-04', N'Corpus Christi'),
    ('DO', '2026-08-16', N'Restoration Day'),
    ('DO', '2026-09-24', N'Our Lady of Mercedes'),
    ('DO', '2026-11-09', N'Constitution Day (moved from Nov 6)'),
    ('DO', '2026-12-25', N'Christmas Day'),
    ('DO', '2027-01-01', N'New Year''s Day'),
    ('DO', '2027-01-04', N'Epiphany (moved from Jan 6)'),
    ('DO', '2027-01-21', N'Our Lady of Altagracia'),
    ('DO', '2027-01-25', N'Duarte Day (moved from Jan 26)'),
    ('DO', '2027-02-27', N'Independence Day'),
    ('DO', '2027-03-26', N'Good Friday'),
    ('DO', '2027-05-01', N'Labor Day'),
    ('DO', '2027-05-27', N'Corpus Christi'),
    ('DO', '2027-08-16', N'Restoration Day'),
    ('DO', '2027-09-24', N'Our Lady of Mercedes'),
    ('DO', '2027-11-06', N'Constitution Day'),
    ('DO', '2027-12-25', N'Christmas Day'),
    -- Puerto Rico (OATRH)
    ('PR', '2026-01-01', N'New Year''s Day'),
    ('PR', '2026-01-06', N'Three Kings Day'),
    ('PR', '2026-01-19', N'Birthday of Martin Luther King, Jr.'),
    ('PR', '2026-02-16', N'Presidents'' Day and Puerto Rican Patriots Day'),
    ('PR', '2026-03-02', N'American Citizenship Day'),
    ('PR', '2026-03-22', N'Emancipation Day'),
    ('PR', '2026-04-03', N'Good Friday'),
    ('PR', '2026-05-25', N'Memorial Day'),
    ('PR', '2026-06-19', N'Juneteenth National Independence Day'),
    ('PR', '2026-07-04', N'Independence Day'),
    ('PR', '2026-07-25', N'Puerto Rico Constitution Day'),
    ('PR', '2026-07-27', N'Jose Celso Barbosa Day'),
    ('PR', '2026-09-07', N'Labor Day'),
    ('PR', '2026-10-12', N'Columbus Day'),
    ('PR', '2026-11-11', N'Veterans Day'),
    ('PR', '2026-11-19', N'Puerto Rican Heritage Day'),
    ('PR', '2026-11-26', N'Thanksgiving Day'),
    ('PR', '2026-12-25', N'Christmas Day'),
    ('PR', '2027-01-01', N'New Year''s Day'),
    ('PR', '2027-01-06', N'Three Kings Day'),
    ('PR', '2027-01-18', N'Birthday of Martin Luther King, Jr.'),
    ('PR', '2027-02-15', N'Presidents'' Day and Puerto Rican Patriots Day'),
    ('PR', '2027-03-02', N'American Citizenship Day'),
    ('PR', '2027-03-22', N'Emancipation Day'),
    ('PR', '2027-03-26', N'Good Friday'),
    ('PR', '2027-05-31', N'Memorial Day'),
    ('PR', '2027-06-19', N'Juneteenth National Independence Day'),
    ('PR', '2027-07-04', N'Independence Day'),
    ('PR', '2027-07-25', N'Puerto Rico Constitution Day'),
    ('PR', '2027-07-27', N'Jose Celso Barbosa Day'),
    ('PR', '2027-09-06', N'Labor Day'),
    ('PR', '2027-10-11', N'Columbus Day'),
    ('PR', '2027-11-11', N'Veterans Day'),
    ('PR', '2027-11-19', N'Puerto Rican Heritage Day'),
    ('PR', '2027-11-25', N'Thanksgiving Day'),
    ('PR', '2027-12-25', N'Christmas Day');

DECLARE @inserted TABLE (holiday_id int, country_id int, [date] varchar(10), name nvarchar(100));
DECLARE @sql nvarchar(max);

BEGIN TRY
    BEGIN TRANSACTION;

    -- a) Resolve countries: matching rows used by employees, else the lowest matching country_id.
    WITH matches AS (
        SELECT DISTINCT a.code, c.country_id
        FROM @aliases a
        JOIN dbo.countries c ON LTRIM(RTRIM(c.name)) COLLATE Latin1_General_CI_AI = a.alias COLLATE Latin1_General_CI_AI
    ), ranked AS (
        SELECT m.code, m.country_id,
               (SELECT COUNT(*) FROM dbo.employees e WHERE e.country_id = m.country_id) AS employees,
               MIN(m.country_id) OVER (PARTITION BY m.code) AS lowest_id
        FROM matches m
    ), with_max AS (
        SELECT r.*, MAX(r.employees) OVER (PARTITION BY r.code) AS max_employees FROM ranked r
    )
    INSERT INTO @countries (code, country_id)
    SELECT code, country_id FROM with_max
    WHERE employees > 0 OR (max_employees = 0 AND country_id = lowest_id);

    IF COLUMNPROPERTY(OBJECT_ID('dbo.countries'), 'country_id', 'IsIdentity') = 1
        INSERT INTO dbo.countries (name)
        SELECT k.name FROM @canonical k WHERE NOT EXISTS (SELECT 1 FROM @countries x WHERE x.code = k.code);
    ELSE
        INSERT INTO dbo.countries (country_id, name)
        SELECT (SELECT ISNULL(MAX(country_id), 0) FROM dbo.countries) + ROW_NUMBER() OVER (ORDER BY k.code), k.name
        FROM @canonical k WHERE NOT EXISTS (SELECT 1 FROM @countries x WHERE x.code = k.code);

    INSERT INTO @countries (code, country_id, created)
    SELECT k.code, MIN(c.country_id), 1
    FROM @canonical k
    JOIN dbo.countries c ON c.name = k.name
    WHERE NOT EXISTS (SELECT 1 FROM @countries x WHERE x.code = k.code)
    GROUP BY k.code;

    -- b) Legacy UNIQUE(date) -> UNIQUE(date, country_id).
    SELECT @sql = STRING_AGG(
        CASE WHEN i.is_unique_constraint = 1
             THEN N'ALTER TABLE dbo.holidays DROP CONSTRAINT ' + QUOTENAME(i.name) + N';'
             ELSE N'DROP INDEX ' + QUOTENAME(i.name) + N' ON dbo.holidays;' END, N' ')
    FROM sys.indexes i
    WHERE i.object_id = OBJECT_ID('dbo.holidays')
      AND i.is_unique = 1
      AND i.is_primary_key = 0
      AND (SELECT COUNT(*) FROM sys.index_columns ic
           WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND ic.is_included_column = 0) = 1
      AND EXISTS (SELECT 1 FROM sys.index_columns ic
                  JOIN sys.columns col ON col.object_id = ic.object_id AND col.column_id = ic.column_id
                  WHERE ic.object_id = i.object_id AND ic.index_id = i.index_id AND col.name = 'date');

    IF @sql IS NOT NULL
    BEGIN
        PRINT 'Replacing legacy unique-on-date: ' + @sql;
        EXEC sp_executesql @sql;
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.holidays') AND name = 'ux_holidays_date_country')
            EXEC sp_executesql N'CREATE UNIQUE INDEX ux_holidays_date_country ON dbo.holidays ([date], country_id);';
    END

    -- c) Insert missing holidays.
    INSERT INTO dbo.holidays (name, [date], [year], country_id)
    OUTPUT inserted.holiday_id, inserted.country_id, inserted.[date], inserted.name INTO @inserted
    SELECT h.name, h.[date], CAST(LEFT(h.[date], 4) AS int), x.country_id
    FROM @holidays h
    JOIN @countries x ON x.code = h.code
    WHERE h.[date] >= @from_date
      AND NOT EXISTS (
          SELECT 1 FROM dbo.holidays e
          WHERE e.[date] = h.[date] AND (e.country_id = x.country_id OR e.country_id IS NULL)
      );

    -- Preview / audit output.
    SELECT x.code, x.country_id, c.name AS country_name, x.created AS country_created
    FROM @countries x JOIN dbo.countries c ON c.country_id = x.country_id
    ORDER BY x.code;

    SELECT x.code, COUNT(i.holiday_id) AS holidays_inserted
    FROM @countries x LEFT JOIN @inserted i ON i.country_id = x.country_id
    GROUP BY x.code ORDER BY x.code;

    SELECT i.[date], x.code, i.name
    FROM @inserted i JOIN @countries x ON x.country_id = i.country_id
    ORDER BY i.[date], x.code;

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
