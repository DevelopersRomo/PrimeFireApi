-- =============================================================================
-- IT Quotation Email Templates
-- Two tables:
--   * it.email_defaults           -> singleton per tenant (fallback template)
--   * it.email_customer_templates -> per-customer override (takes precedence)
--
-- Registers a new module `it_email_templates` and grants Admin permissions.
-- =============================================================================

SET NOCOUNT ON;
GO

-- 1. Tenant-wide default template (one row per tenant).
IF OBJECT_ID('it.email_defaults', 'U') IS NULL
BEGIN
    CREATE TABLE it.email_defaults (
        default_id  INT IDENTITY PRIMARY KEY,
        tenant_id   INT           NOT NULL,
        subject     NVARCHAR(300) NOT NULL,
        title       NVARCHAR(300) NOT NULL,
        message_body NVARCHAR(MAX) NOT NULL,
        footer      NVARCHAR(1000) NULL,
        logo_path   NVARCHAR(1000) NULL,
        is_active   BIT           NOT NULL DEFAULT 1,
        created_at  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_email_defaults_tenant UNIQUE (tenant_id)
    );
END;
GO

-- 2. Per-customer override (0..1 per customer).
IF OBJECT_ID('it.email_customer_templates', 'U') IS NULL
BEGIN
    CREATE TABLE it.email_customer_templates (
        template_id INT IDENTITY PRIMARY KEY,
        tenant_id   INT           NOT NULL,
        customer_id INT           NOT NULL,
        subject     NVARCHAR(300) NOT NULL,
        title       NVARCHAR(300) NOT NULL,
        message_body NVARCHAR(MAX) NOT NULL,
        footer      NVARCHAR(1000) NULL,
        logo_path   NVARCHAR(1000) NULL,
        is_active   BIT           NOT NULL DEFAULT 1,
        created_at  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_email_customer_templates_tenant_customer
            UNIQUE (tenant_id, customer_id)
    );
END;
GO

-- 3. Register the new module so it can appear in the menu and RBAC.
DECLARE @email_module_key NVARCHAR(50)  = 'it_email_templates';
DECLARE @email_module_name NVARCHAR(50) = 'IT Email Templates';
DECLARE @email_module_route NVARCHAR(100) = '/it/email-templates';
DECLARE @email_module_icon NVARCHAR(50) = 'mail';
DECLARE @email_module_order INT = 86;

IF NOT EXISTS (SELECT 1 FROM dbo.modules WHERE module_key = @email_module_key)
BEGIN
    INSERT INTO dbo.modules (module_name, module_key, description, icon, route_url, display_order, is_active)
    VALUES (@email_module_name, @email_module_key, @email_module_name,
            @email_module_icon, @email_module_route, @email_module_order, 1);
END;
GO

-- 4. Grant full permissions to Admin roles.
INSERT INTO dbo.role_modules (role_id, module_id, can_view, can_create, can_edit, can_delete, can_export, admin_actions, other_actions)
SELECT r.role_id, dm.module_id, 1, 1, 1, 1, 1, 1, 1
FROM dbo.roles r
CROSS JOIN dbo.modules dm
WHERE r.role_name IN ('Admin', 'Administrator')
  AND dm.module_key = 'it_email_templates'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.role_modules rm
      WHERE rm.role_id = r.role_id AND rm.module_id = dm.module_id
  );
GO

PRINT 'IT email templates schema created successfully.';
GO
