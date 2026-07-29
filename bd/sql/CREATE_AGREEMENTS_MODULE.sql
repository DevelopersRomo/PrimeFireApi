SET XACT_ABORT ON;
BEGIN TRANSACTION;

IF OBJECT_ID('dbo.agreements', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.agreements (
        agreement_id int IDENTITY(1,1) NOT NULL CONSTRAINT pk_agreements PRIMARY KEY,
        title varchar(250) NOT NULL,
        agreement_type varchar(40) NOT NULL,
        customer_id int NULL,
        counterparty_name varchar(250) NOT NULL,
        owner_employee_id int NOT NULL,
        effective_date date NOT NULL,
        expiration_date date NULL,
        terminated_on date NULL,
        termination_reason varchar(1000) NULL,
        terminated_by int NULL,
        notes varchar(max) NULL,
        created_at datetime2 NOT NULL CONSTRAINT df_agreements_created_at DEFAULT SYSUTCDATETIME(),
        created_by int NOT NULL,
        updated_at datetime2 NULL,
        updated_by int NULL,
        archived_at datetime2 NULL,
        archived_by int NULL,
        CONSTRAINT ck_agreements_type CHECK (agreement_type IN ('SERVICE_AGREEMENT', 'MASTER_SERVICE_AGREEMENT', 'NDA', 'MAINTENANCE_AGREEMENT', 'OTHER')),
        CONSTRAINT ck_agreements_dates CHECK (expiration_date IS NULL OR expiration_date >= effective_date),
        CONSTRAINT ck_agreements_termination CHECK ((terminated_on IS NULL AND termination_reason IS NULL) OR (terminated_on IS NOT NULL AND termination_reason IS NOT NULL)),
        CONSTRAINT fk_agreements_customer FOREIGN KEY (customer_id) REFERENCES dbo.customers(customer_id),
        CONSTRAINT fk_agreements_owner FOREIGN KEY (owner_employee_id) REFERENCES dbo.employees(employee_id),
        CONSTRAINT fk_agreements_created_by FOREIGN KEY (created_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT fk_agreements_updated_by FOREIGN KEY (updated_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT fk_agreements_archived_by FOREIGN KEY (archived_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT fk_agreements_terminated_by FOREIGN KEY (terminated_by) REFERENCES dbo.employees(employee_id)
    );

    CREATE INDEX ix_agreements_list ON dbo.agreements(archived_at, effective_date, expiration_date);
    CREATE INDEX ix_agreements_customer ON dbo.agreements(customer_id);
    CREATE INDEX ix_agreements_owner ON dbo.agreements(owner_employee_id);
    CREATE INDEX ix_agreements_counterparty ON dbo.agreements(counterparty_name);
END;

IF OBJECT_ID('dbo.agreement_attachments', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.agreement_attachments (
        agreement_attachment_id int IDENTITY(1,1) NOT NULL CONSTRAINT pk_agreement_attachments PRIMARY KEY,
        agreement_id int NOT NULL,
        attachment_type varchar(20) NOT NULL,
        version_number int NULL,
        is_current bit NOT NULL CONSTRAINT df_agreement_attachments_current DEFAULT 0,
        replacement_reason varchar(1000) NULL,
        original_filename varchar(255) NOT NULL,
        stored_filename varchar(100) NOT NULL,
        storage_path varchar(500) NOT NULL,
        file_extension varchar(10) NOT NULL,
        mime_type varchar(150) NOT NULL,
        file_size bigint NOT NULL,
        sha256 char(64) NOT NULL,
        created_at datetime2 NOT NULL CONSTRAINT df_agreement_attachments_created_at DEFAULT SYSUTCDATETIME(),
        created_by int NOT NULL,
        archived_at datetime2 NULL,
        archived_by int NULL,
        CONSTRAINT ck_agreement_attachment_type CHECK (attachment_type IN ('PRIMARY', 'SUPPORTING')),
        CONSTRAINT ck_agreement_attachment_size CHECK (file_size > 0 AND file_size <= 26214400),
        CONSTRAINT ck_agreement_attachment_version CHECK ((attachment_type = 'PRIMARY' AND version_number IS NOT NULL) OR (attachment_type = 'SUPPORTING' AND version_number IS NULL)),
        CONSTRAINT fk_agreement_attachments_agreement FOREIGN KEY (agreement_id) REFERENCES dbo.agreements(agreement_id),
        CONSTRAINT fk_agreement_attachments_created_by FOREIGN KEY (created_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT fk_agreement_attachments_archived_by FOREIGN KEY (archived_by) REFERENCES dbo.employees(employee_id)
    );

    CREATE UNIQUE INDEX ux_agreement_primary_version ON dbo.agreement_attachments(agreement_id, version_number) WHERE attachment_type = 'PRIMARY';
    CREATE UNIQUE INDEX ux_agreement_current_primary ON dbo.agreement_attachments(agreement_id) WHERE attachment_type = 'PRIMARY' AND is_current = 1;
    CREATE INDEX ix_agreement_attachments_filename ON dbo.agreement_attachments(original_filename);
END;

DECLARE @now varchar(19) = CONVERT(varchar(19), SYSUTCDATETIME(), 120);
DECLARE @parent_module_id int;
DECLARE @agreements_module_id int;
DECLARE @customers_module_id int;

UPDATE dbo.modules
SET created_at = @now
WHERE created_at IS NULL;

SELECT @parent_module_id = module_id FROM dbo.modules WHERE module_key = 'business-proposals';
SELECT @customers_module_id = module_id FROM dbo.modules WHERE module_key = 'customers';

IF @parent_module_id IS NULL
BEGIN
    INSERT INTO dbo.modules (module_name, module_key, description, icon, route_url, display_order, is_active, parent_module_id, created_at)
    VALUES ('Business Proposals', 'business-proposals', 'Business proposals', 'request_quote', '', 0, 1, NULL, @now);
    SET @parent_module_id = SCOPE_IDENTITY();
END;

SELECT @agreements_module_id = module_id FROM dbo.modules WHERE module_key = 'agreements';

IF @agreements_module_id IS NULL
BEGIN
    INSERT INTO dbo.modules (module_name, module_key, description, icon, route_url, display_order, is_active, parent_module_id, created_at)
    VALUES ('Agreements', 'agreements', 'Formalized agreement repository', 'contract', '/agreements', 9, 1, @parent_module_id, @now);
    SET @agreements_module_id = SCOPE_IDENTITY();
END
ELSE
BEGIN
    UPDATE dbo.modules
    SET module_name = 'Agreements', description = 'Formalized agreement repository', icon = 'contract', route_url = '/agreements',
        display_order = 9, is_active = 1, parent_module_id = @parent_module_id
    WHERE module_id = @agreements_module_id;
END;

UPDATE agreements_permissions
SET can_view = customer_permissions.can_view,
    can_create = customer_permissions.can_create,
    can_edit = customer_permissions.can_edit,
    can_delete = customer_permissions.can_delete,
    can_export = customer_permissions.can_export,
    admin_actions = customer_permissions.admin_actions,
    other_actions = customer_permissions.other_actions,
    assigned_at = SYSUTCDATETIME()
FROM dbo.role_modules AS agreements_permissions
INNER JOIN dbo.role_modules AS parent_permissions
    ON parent_permissions.role_id = agreements_permissions.role_id
   AND parent_permissions.module_id = @parent_module_id
INNER JOIN dbo.role_modules AS customer_permissions
    ON customer_permissions.role_id = agreements_permissions.role_id
   AND customer_permissions.module_id = @customers_module_id
WHERE agreements_permissions.module_id = @agreements_module_id
  AND agreements_permissions.can_view = parent_permissions.can_view
  AND agreements_permissions.can_create = parent_permissions.can_create
  AND agreements_permissions.can_edit = parent_permissions.can_edit
  AND agreements_permissions.can_delete = parent_permissions.can_delete
  AND agreements_permissions.can_export = parent_permissions.can_export
  AND agreements_permissions.admin_actions = parent_permissions.admin_actions
  AND agreements_permissions.other_actions = parent_permissions.other_actions;

INSERT INTO dbo.role_modules (role_id, module_id, can_view, can_create, can_edit, can_delete, can_export, admin_actions, other_actions, assigned_at)
SELECT role_id, @agreements_module_id, can_view, can_create, can_edit, can_delete, can_export, admin_actions, other_actions, SYSUTCDATETIME()
FROM dbo.role_modules AS customer_permissions
WHERE customer_permissions.module_id = @customers_module_id
  AND NOT EXISTS (
      SELECT 1 FROM dbo.role_modules existing
      WHERE existing.role_id = customer_permissions.role_id AND existing.module_id = @agreements_module_id
  );

COMMIT TRANSACTION;
