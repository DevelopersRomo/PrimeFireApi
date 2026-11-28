-- Home posts created from SQLModel metadata got VARCHAR columns, which store emoji as "?".
-- Widening to NVARCHAR keeps existing text. Safe to run more than once, on any tenant database.
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'home_posts' AND COLUMN_NAME = 'title' AND DATA_TYPE = 'varchar')
    ALTER TABLE dbo.home_posts ALTER COLUMN title NVARCHAR(200) NOT NULL;

IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'home_posts' AND COLUMN_NAME = 'body_html' AND DATA_TYPE = 'varchar')
    ALTER TABLE dbo.home_posts ALTER COLUMN body_html NVARCHAR(MAX) NOT NULL;

IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'home_posts' AND COLUMN_NAME = 'location' AND DATA_TYPE = 'varchar')
    ALTER TABLE dbo.home_posts ALTER COLUMN location NVARCHAR(200) NULL;
