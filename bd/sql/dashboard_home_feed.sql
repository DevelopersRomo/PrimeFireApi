-- Dashboard home feed: holidays per country + home posts (news/events).
--
-- Run this ONE file against EVERY database:
--   1. Main database (DB_DATABASE)
--   2. Each tenant database
-- Idempotent: safe to run more than once. GO separates the batches, so run it in
-- SSMS / Azure Data Studio / sqlcmd (not as a single query through a driver).
--
-- Order matters: 1) holidays.country_id  2) Holidays module
--                3) home_posts table     4) Home Posts module

-- =====================================================================
-- 1) holidays.country_id
-- =====================================================================
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.holidays')
    AND name = 'country_id'
)
BEGIN
    ALTER TABLE [dbo].[holidays] ADD [country_id] INT NULL;
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'fk_holidays_country_id'
    AND parent_object_id = OBJECT_ID('dbo.holidays')
)
BEGIN
    ALTER TABLE [dbo].[holidays]
        ADD CONSTRAINT [fk_holidays_country_id]
        FOREIGN KEY ([country_id]) REFERENCES [dbo].[countries] ([country_id]);
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'ix_holidays_country_id'
    AND object_id = OBJECT_ID('dbo.holidays')
)
BEGIN
    CREATE INDEX [ix_holidays_country_id] ON [dbo].[holidays] ([country_id]);
END
GO

-- =====================================================================
-- 2) Holidays module (Configuration > Holidays) + Admin grant
-- =====================================================================
DECLARE @now varchar(19) = CONVERT(varchar(19), SYSUTCDATETIME(), 120);
DECLARE @parent_module_id int = (SELECT module_id FROM dbo.modules WHERE module_key = 'administration');

IF NOT EXISTS (SELECT 1 FROM dbo.modules WHERE module_key = 'holidays')
BEGIN
    INSERT INTO dbo.modules (
        module_name,
        module_key,
        description,
        icon,
        route_url,
        display_order,
        is_active,
        parent_module_id,
        created_at
    )
    VALUES (
        'Holidays',
        'holidays',
        'Public holidays per country',
        'event',
        '/config/holidays',
        10,
        1,
        @parent_module_id,
        @now
    );
END;

DECLARE @holidays_module_id int = (SELECT module_id FROM dbo.modules WHERE module_key = 'holidays');

INSERT INTO dbo.role_modules (
    role_id,
    module_id,
    can_view,
    can_create,
    can_edit,
    can_delete,
    can_export,
    admin_actions,
    other_actions,
    assigned_at
)
SELECT r.role_id, @holidays_module_id, 1, 1, 1, 1, 1, 1, 0, SYSUTCDATETIME()
FROM dbo.roles r
WHERE LOWER(LTRIM(RTRIM(r.role_name))) = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.role_modules existing
      WHERE existing.role_id = r.role_id
        AND existing.module_id = @holidays_module_id
  );
GO

-- =====================================================================
-- 3) home_posts table
-- =====================================================================
IF OBJECT_ID('dbo.home_posts', 'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[home_posts] (
        [post_id] INT IDENTITY(1,1) NOT NULL,
        [title] NVARCHAR(200) NOT NULL,
        [post_type] NVARCHAR(10) NOT NULL,
        [body_html] NVARCHAR(MAX) NOT NULL,
        [event_at] DATETIME NULL,
        [location] NVARCHAR(200) NULL,
        [cover_path] NVARCHAR(500) NULL,
        [cover_content_type] NVARCHAR(50) NULL,
        [is_pinned] BIT NOT NULL CONSTRAINT [df_home_posts_is_pinned] DEFAULT (0),
        [published_at] DATETIME NULL,
        [expires_at] DATETIME NULL,
        [created_by] INT NULL,
        [created_at] DATETIME NOT NULL CONSTRAINT [df_home_posts_created_at] DEFAULT (SYSUTCDATETIME()),
        [updated_at] DATETIME NOT NULL CONSTRAINT [df_home_posts_updated_at] DEFAULT (SYSUTCDATETIME()),
        [is_active] BIT NOT NULL CONSTRAINT [df_home_posts_is_active] DEFAULT (1),
        CONSTRAINT [pk_home_posts] PRIMARY KEY CLUSTERED ([post_id]),
        CONSTRAINT [ck_home_posts_post_type] CHECK ([post_type] IN ('news', 'event')),
        CONSTRAINT [fk_home_posts_created_by]
            FOREIGN KEY ([created_by]) REFERENCES [dbo].[employees] ([employee_id])
    );
END
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'ix_home_posts_active_published'
    AND object_id = OBJECT_ID('dbo.home_posts')
)
BEGIN
    CREATE INDEX [ix_home_posts_active_published] ON [dbo].[home_posts] ([is_active], [published_at]);
END
GO

-- =====================================================================
-- 4) Home Posts module (Configuration > Home Posts) + Admin grant
-- =====================================================================
DECLARE @now varchar(19) = CONVERT(varchar(19), SYSUTCDATETIME(), 120);
DECLARE @parent_module_id int = (SELECT module_id FROM dbo.modules WHERE module_key = 'administration');

IF NOT EXISTS (SELECT 1 FROM dbo.modules WHERE module_key = 'home_posts')
BEGIN
    INSERT INTO dbo.modules (
        module_name,
        module_key,
        description,
        icon,
        route_url,
        display_order,
        is_active,
        parent_module_id,
        created_at
    )
    VALUES (
        'Home Posts',
        'home_posts',
        'Company news and events shown on the dashboard',
        'campaign',
        '/config/home-posts',
        11,
        1,
        @parent_module_id,
        @now
    );
END;

DECLARE @home_posts_module_id int = (SELECT module_id FROM dbo.modules WHERE module_key = 'home_posts');

INSERT INTO dbo.role_modules (
    role_id,
    module_id,
    can_view,
    can_create,
    can_edit,
    can_delete,
    can_export,
    admin_actions,
    other_actions,
    assigned_at
)
SELECT r.role_id, @home_posts_module_id, 1, 1, 1, 1, 1, 1, 0, SYSUTCDATETIME()
FROM dbo.roles r
WHERE LOWER(LTRIM(RTRIM(r.role_name))) = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.role_modules existing
      WHERE existing.role_id = r.role_id
        AND existing.module_id = @home_posts_module_id
  );
GO
