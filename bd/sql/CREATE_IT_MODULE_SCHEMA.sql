-- =============================================================================
-- IT Solutions Module - schema, tables, indexes and permission seeds
-- Idempotent: safe to run multiple times.
-- Run against each tenant database that should have the IT module.
-- =============================================================================

-- 1. Schema
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'it')
BEGIN
    -- No AUTHORIZATION clause: some environments (e.g. Azure SQL / contained
    -- users) reject "AUTHORIZATION dbo" with Msg 15151.
    EXEC('CREATE SCHEMA it');
END;
GO

-- 2. Quotation number sequence
IF NOT EXISTS (
    SELECT 1 FROM sys.sequences s
    JOIN sys.schemas sc ON sc.schema_id = s.schema_id
    WHERE s.name = 'quotation_sequence' AND sc.name = 'it'
)
BEGIN
    CREATE SEQUENCE it.quotation_sequence AS BIGINT START WITH 1 INCREMENT BY 1;
END;
GO

-- 3. Categories
IF OBJECT_ID('it.categories', 'U') IS NULL
BEGIN
    CREATE TABLE it.categories (
        category_id INT IDENTITY PRIMARY KEY,
        tenant_id INT NOT NULL,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(500) NULL,
        item_type VARCHAR(30) NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NULL,
        CONSTRAINT CK_it_categories_item_type CHECK (
            item_type IS NULL OR item_type IN (
                'SERVICE', 'LICENSE', 'HOSTING', 'DOMAIN', 'SSL',
                'SUBSCRIPTION', 'SUPPORT', 'OTHER'
            )
        )
    );
END;
GO

-- 4. Catalog items
IF OBJECT_ID('it.catalog_items', 'U') IS NULL
BEGIN
    CREATE TABLE it.catalog_items (
        catalog_item_id INT IDENTITY PRIMARY KEY,
        tenant_id INT NOT NULL,
        category_id INT NULL,
        item_type VARCHAR(30) NOT NULL,
        code NVARCHAR(100) NULL,
        sku NVARCHAR(100) NULL,
        name NVARCHAR(200) NOT NULL,
        description NVARCHAR(2000) NULL,
        unit NVARCHAR(50) NOT NULL DEFAULT 'EA',
        billing_cycle VARCHAR(20) NOT NULL DEFAULT 'ONE_TIME',
        currency CHAR(3) NOT NULL DEFAULT 'USD',
        unit_price DECIMAL(18,2) NOT NULL DEFAULT 0,
        cost DECIMAL(18,2) NOT NULL DEFAULT 0,
        tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
        scope_template NVARCHAR(MAX) NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_by INT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NULL,
        CONSTRAINT FK_it_catalog_items_category
            FOREIGN KEY (category_id) REFERENCES it.categories(category_id),
        CONSTRAINT FK_it_catalog_items_employee
            FOREIGN KEY (created_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT CK_it_catalog_items_type CHECK (
            item_type IN (
                'SERVICE', 'LICENSE', 'HOSTING', 'DOMAIN', 'SSL',
                'SUBSCRIPTION', 'SUPPORT', 'OTHER'
            )
        ),
        CONSTRAINT CK_it_catalog_items_billing_cycle CHECK (
            billing_cycle IN ('ONE_TIME', 'MONTHLY', 'QUARTERLY', 'ANNUAL')
        ),
        CONSTRAINT CK_it_catalog_items_prices CHECK (
            unit_price >= 0 AND cost >= 0 AND tax_rate >= 0
        )
    );

    CREATE UNIQUE INDEX UX_it_catalog_items_tenant_code
        ON it.catalog_items (tenant_id, code)
        WHERE code IS NOT NULL;

    CREATE INDEX IX_it_catalog_items_tenant_type
        ON it.catalog_items (tenant_id, item_type);
END;
GO

-- 5. Service details (1:1 with catalog item)
IF OBJECT_ID('it.service_details', 'U') IS NULL
BEGIN
    CREATE TABLE it.service_details (
        catalog_item_id INT PRIMARY KEY,
        estimated_delivery_days INT NULL,
        included_hours DECIMAL(10,2) NULL,
        deliverables NVARCHAR(MAX) NULL,
        exclusions NVARCHAR(MAX) NULL,
        technical_requirements NVARCHAR(MAX) NULL,
        CONSTRAINT FK_it_service_details_catalog
            FOREIGN KEY (catalog_item_id) REFERENCES it.catalog_items(catalog_item_id)
            ON DELETE CASCADE,
        CONSTRAINT CK_it_service_delivery_days CHECK (
            estimated_delivery_days IS NULL OR estimated_delivery_days >= 0
        )
    );
END;
GO

-- 6. License details (1:1 with catalog item)
IF OBJECT_ID('it.license_details', 'U') IS NULL
BEGIN
    CREATE TABLE it.license_details (
        catalog_item_id INT PRIMARY KEY,
        vendor NVARCHAR(150) NULL,
        vendor_product_code NVARCHAR(100) NULL,
        license_type VARCHAR(30) NULL,
        default_seats INT NULL,
        term_months INT NULL,
        auto_renew BIT NOT NULL DEFAULT 0,
        procurement_notes NVARCHAR(1000) NULL,
        CONSTRAINT FK_it_license_details_catalog
            FOREIGN KEY (catalog_item_id) REFERENCES it.catalog_items(catalog_item_id)
            ON DELETE CASCADE,
        CONSTRAINT CK_it_license_type CHECK (
            license_type IS NULL OR license_type IN (
                'PER_USER', 'PER_DEVICE', 'SITE', 'SUBSCRIPTION'
            )
        ),
        CONSTRAINT CK_it_license_seats CHECK (default_seats IS NULL OR default_seats >= 0),
        CONSTRAINT CK_it_license_term CHECK (term_months IS NULL OR term_months > 0)
    );
END;
GO

-- 7. PDF templates
IF OBJECT_ID('it.pdf_templates', 'U') IS NULL
BEGIN
    CREATE TABLE it.pdf_templates (
        template_id INT IDENTITY PRIMARY KEY,
        tenant_id INT NOT NULL,
        name NVARCHAR(150) NOT NULL,
        template_key NVARCHAR(100) NOT NULL,
        company_name NVARCHAR(200) NOT NULL,
        logo_url NVARCHAR(500) NULL,
        primary_color NVARCHAR(20) NULL,
        secondary_color NVARCHAR(20) NULL,
        address_text NVARCHAR(500) NULL,
        phone NVARCHAR(50) NULL,
        email NVARCHAR(150) NULL,
        website NVARCHAR(200) NULL,
        default_footer NVARCHAR(1000) NULL,
        signature_name NVARCHAR(150) NULL,
        signature_title NVARCHAR(150) NULL,
        signature_image_url NVARCHAR(500) NULL,
        is_default BIT NOT NULL DEFAULT 0,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
GO

-- 8. Quotations header
IF OBJECT_ID('it.quotations', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotations (
        quotation_id INT IDENTITY PRIMARY KEY,
        tenant_id INT NOT NULL,
        customer_id INT NOT NULL,
        contact_id INT NULL,
        quotation_number NVARCHAR(50) NOT NULL,
        status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
        quote_date DATE NOT NULL,
        expiration_date DATE NOT NULL,
        currency CHAR(3) NOT NULL DEFAULT 'USD',
        customer_name_snapshot NVARCHAR(200) NOT NULL,
        contact_name_snapshot NVARCHAR(200) NULL,
        customer_email_snapshot NVARCHAR(200) NULL,
        customer_address_snapshot NVARCHAR(1000) NULL,
        one_time_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
        monthly_recurring_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
        annual_recurring_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
        discount_total DECIMAL(18,2) NOT NULL DEFAULT 0,
        tax_total DECIMAL(18,2) NOT NULL DEFAULT 0,
        initial_total DECIMAL(18,2) NOT NULL DEFAULT 0,
        visible_notes NVARCHAR(MAX) NULL,
        internal_notes NVARCHAR(MAX) NULL,
        template_id INT NULL,
        owner_employee_id INT NULL,
        created_by INT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NULL,
        sent_at DATETIME2 NULL,
        accepted_at DATETIME2 NULL,
        rejected_at DATETIME2 NULL,
        row_version ROWVERSION,
        CONSTRAINT FK_it_quotations_customer
            FOREIGN KEY (customer_id) REFERENCES dbo.customers(customer_id),
        CONSTRAINT FK_it_quotations_contact
            FOREIGN KEY (contact_id) REFERENCES dbo.customer_alternate_contacts(customer_alternate_contact_id),
        CONSTRAINT FK_it_quotations_template
            FOREIGN KEY (template_id) REFERENCES it.pdf_templates(template_id),
        CONSTRAINT FK_it_quotations_owner
            FOREIGN KEY (owner_employee_id) REFERENCES dbo.employees(employee_id),
        CONSTRAINT FK_it_quotations_created_by
            FOREIGN KEY (created_by) REFERENCES dbo.employees(employee_id),
        CONSTRAINT CK_it_quotations_status CHECK (
            status IN ('DRAFT', 'SENT', 'VIEWED', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CANCELLED')
        ),
        CONSTRAINT CK_it_quotations_totals CHECK (
            one_time_subtotal >= 0 AND monthly_recurring_subtotal >= 0
            AND annual_recurring_subtotal >= 0 AND discount_total >= 0
            AND tax_total >= 0 AND initial_total >= 0
        )
    );

    CREATE UNIQUE INDEX UX_it_quotations_tenant_number
        ON it.quotations (tenant_id, quotation_number);

    CREATE INDEX IX_it_quotations_tenant_status ON it.quotations (tenant_id, status);
    CREATE INDEX IX_it_quotations_customer ON it.quotations (customer_id);
END;
GO

-- 9. Quotation items
IF OBJECT_ID('it.quotation_items', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotation_items (
        quotation_item_id INT IDENTITY PRIMARY KEY,
        quotation_id INT NOT NULL,
        catalog_item_id INT NULL,
        item_type VARCHAR(30) NOT NULL,
        billing_cycle VARCHAR(20) NOT NULL,
        code_snapshot NVARCHAR(100) NULL,
        name_snapshot NVARCHAR(200) NOT NULL,
        description_snapshot NVARCHAR(2000) NULL,
        scope_snapshot NVARCHAR(MAX) NULL,
        quantity DECIMAL(18,2) NOT NULL DEFAULT 1,
        unit NVARCHAR(50) NOT NULL DEFAULT 'EA',
        unit_price DECIMAL(18,2) NOT NULL DEFAULT 0,
        discount_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
        tax_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
        line_subtotal DECIMAL(18,2) NOT NULL DEFAULT 0,
        line_discount DECIMAL(18,2) NOT NULL DEFAULT 0,
        line_tax DECIMAL(18,2) NOT NULL DEFAULT 0,
        line_total DECIMAL(18,2) NOT NULL DEFAULT 0,
        term_months INT NULL,
        sort_order INT NOT NULL DEFAULT 0,
        CONSTRAINT FK_it_quotation_items_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT FK_it_quotation_items_catalog
            FOREIGN KEY (catalog_item_id) REFERENCES it.catalog_items(catalog_item_id),
        CONSTRAINT CK_it_quotation_items_quantity CHECK (quantity > 0),
        CONSTRAINT CK_it_quotation_items_billing CHECK (
            billing_cycle IN ('ONE_TIME', 'MONTHLY', 'QUARTERLY', 'ANNUAL')
        )
    );

    CREATE INDEX IX_it_quotation_items_quotation ON it.quotation_items (quotation_id);
END;
GO

-- 10. Quotation terms (1:1 with quotation)
IF OBJECT_ID('it.quotation_terms', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotation_terms (
        quotation_id INT PRIMARY KEY,
        delivery_time_text NVARCHAR(500) NULL,
        validity_days INT NULL,
        payment_terms_text NVARCHAR(MAX) NULL,
        exclusions_text NVARCHAR(MAX) NULL,
        tax_note NVARCHAR(MAX) NULL,
        recurring_note NVARCHAR(MAX) NULL,
        warranty_text NVARCHAR(MAX) NULL,
        acceptance_text NVARCHAR(MAX) NULL,
        CONSTRAINT FK_it_quotation_terms_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT CK_it_quotation_terms_validity CHECK (
            validity_days IS NULL OR validity_days > 0
        )
    );
END;
GO

-- 11. Payment schedule
IF OBJECT_ID('it.payment_schedule', 'U') IS NULL
BEGIN
    CREATE TABLE it.payment_schedule (
        payment_schedule_id INT IDENTITY PRIMARY KEY,
        quotation_id INT NOT NULL,
        sequence_number INT NOT NULL,
        description NVARCHAR(250) NOT NULL,
        percentage DECIMAL(5,2) NULL,
        amount DECIMAL(18,2) NULL,
        due_rule NVARCHAR(250) NULL,
        CONSTRAINT FK_it_payment_schedule_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT CK_it_payment_percentage CHECK (
            percentage IS NULL OR (percentage > 0 AND percentage <= 100)
        ),
        CONSTRAINT CK_it_payment_amount CHECK (amount IS NULL OR amount >= 0)
    );

    CREATE UNIQUE INDEX UX_it_payment_schedule_sequence
        ON it.payment_schedule (quotation_id, sequence_number);
END;
GO

-- 12. Quotation documents (PDF versions)
IF OBJECT_ID('it.quotation_documents', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotation_documents (
        document_id INT IDENTITY PRIMARY KEY,
        quotation_id INT NOT NULL,
        document_type VARCHAR(30) NOT NULL DEFAULT 'PDF',
        file_name NVARCHAR(255) NOT NULL,
        storage_path NVARCHAR(1000) NOT NULL,
        document_version INT NOT NULL DEFAULT 1,
        file_hash NVARCHAR(128) NULL,
        generated_by INT NULL,
        generated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_it_documents_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT FK_it_documents_employee
            FOREIGN KEY (generated_by) REFERENCES dbo.employees(employee_id)
    );

    CREATE INDEX IX_it_documents_quotation ON it.quotation_documents (quotation_id);
END;
GO

-- 12b. Quotation internal notes (many per quotation)
IF OBJECT_ID('it.quotation_notes', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotation_notes (
        note_id INT IDENTITY PRIMARY KEY,
        quotation_id INT NOT NULL,
        note_text NVARCHAR(MAX) NOT NULL,
        created_by INT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_it_quotation_notes_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT FK_it_quotation_notes_employee
            FOREIGN KEY (created_by) REFERENCES dbo.employees(employee_id)
    );

    CREATE INDEX IX_it_quotation_notes_quotation ON it.quotation_notes (quotation_id);
END;
GO

-- 13. Quotation status history
IF OBJECT_ID('it.quotation_status_history', 'U') IS NULL
BEGIN
    CREATE TABLE it.quotation_status_history (
        history_id INT IDENTITY PRIMARY KEY,
        quotation_id INT NOT NULL,
        previous_status VARCHAR(30) NULL,
        new_status VARCHAR(30) NOT NULL,
        changed_by INT NULL,
        change_notes NVARCHAR(500) NULL,
        changed_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_it_quote_history_quotation
            FOREIGN KEY (quotation_id) REFERENCES it.quotations(quotation_id)
            ON DELETE CASCADE,
        CONSTRAINT FK_it_quote_history_employee
            FOREIGN KEY (changed_by) REFERENCES dbo.employees(employee_id)
    );

    CREATE INDEX IX_it_quote_history_quotation ON it.quotation_status_history (quotation_id);
END;
GO

-- 14. Module and permission seeds
-- Creates the six IT module keys and grants full access to the Admin role.
DECLARE @modules TABLE (
    module_key NVARCHAR(50),
    module_name NVARCHAR(50),
    route_url NVARCHAR(100),
    icon NVARCHAR(50),
    display_order INT
);

INSERT INTO @modules (module_key, module_name, route_url, icon, display_order)
VALUES
    ('it_dashboard',  'IT Overview',        '/it',            'computer',       80),
    ('it_catalog',    'IT Services Catalog','/it/catalog',    'design_services',81),
    ('it_licenses',   'IT Licenses',        '/it/licenses',   'key',            82),
    ('it_quotations', 'IT Quotations',      '/it/quotations', 'request_quote',  83),
    ('it_templates',  'IT PDF Templates',   '/it/templates',  'picture_as_pdf', 84),
    ('it_documents',  'IT Documents',       '/it/documents',  'folder',         85);

INSERT INTO dbo.modules (module_name, module_key, description, icon, route_url, display_order, is_active)
SELECT m.module_name, m.module_key, m.module_name, m.icon, m.route_url, m.display_order, 1
FROM @modules m
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.modules dm WHERE dm.module_key = m.module_key
);

-- Grant full permissions to Admin role(s)
INSERT INTO dbo.role_modules (role_id, module_id, can_view, can_create, can_edit, can_delete, can_export, admin_actions, other_actions)
SELECT r.role_id, dm.module_id, 1, 1, 1, 1, 1, 1, 1
FROM dbo.roles r
CROSS JOIN dbo.modules dm
WHERE r.role_name IN ('Admin', 'Administrator')
  AND dm.module_key IN ('it_dashboard', 'it_catalog', 'it_licenses', 'it_quotations', 'it_templates', 'it_documents')
  AND NOT EXISTS (
      SELECT 1 FROM dbo.role_modules rm
      WHERE rm.role_id = r.role_id AND rm.module_id = dm.module_id
  );
GO

PRINT 'IT module schema created successfully.';
GO
