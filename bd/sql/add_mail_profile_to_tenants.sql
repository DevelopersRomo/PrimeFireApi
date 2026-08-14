-- Migration: Add mail_profile column to tenants table
-- Holds the named mail profile key that selects which Microsoft tenant sends this
-- tenant's outbound mail. The key maps to environment variables by convention:
--   devromo_tenant -> DEVROMO_TENANT_TENANT_ID / _CLIENT_ID / _CLIENT_SECRET / _BOT_EMAIL
-- The reserved key 'default' means the legacy MICROSOFT_* credentials and BOT_EMAIL,
-- which is also what any profile with an incomplete env block falls back to.
IF NOT EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tenants')
    AND name = 'mail_profile'
)
BEGIN
    ALTER TABLE [dbo].[tenants]
    ADD [mail_profile] VARCHAR(50) NOT NULL
        CONSTRAINT [df_tenants_mail_profile] DEFAULT ('default');
END
GO

-- Widen the column if an earlier revision of this migration created it at 20 chars.
IF EXISTS (
    SELECT 1
    FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.tenants')
    AND name = 'mail_profile'
    AND max_length < 50
)
BEGIN
    ALTER TABLE [dbo].[tenants]
    ALTER COLUMN [mail_profile] VARCHAR(50) NOT NULL;
END
GO

-- Seed the known tenants with their named profile keys.
UPDATE [dbo].[tenants] SET [mail_profile] = 'devromo_tenant'
WHERE [name] = 'DevRomo' AND [mail_profile] <> 'devromo_tenant';
GO

UPDATE [dbo].[tenants] SET [mail_profile] = 'primefire_tenant'
WHERE [name] = 'PrimeFire' AND [mail_profile] <> 'primefire_tenant';
GO
