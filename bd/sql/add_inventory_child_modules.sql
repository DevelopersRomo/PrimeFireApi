DECLARE @now varchar(19) = CONVERT(varchar(19), SYSUTCDATETIME(), 120);
DECLARE @inventory_module_id int;

SELECT @inventory_module_id = module_id
FROM dbo.modules
WHERE module_key = 'inventory';

IF @inventory_module_id IS NULL
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
        'Inventory',
        'inventory',
        'Inventory management',
        'inventory_2',
        '/inventory',
        60,
        1,
        NULL,
        @now
    );

    SET @inventory_module_id = SCOPE_IDENTITY();
END;

UPDATE dbo.modules
SET icon = COALESCE(NULLIF(icon, ''), 'inventory_2'),
    route_url = COALESCE(NULLIF(route_url, ''), '/inventory')
WHERE module_id = @inventory_module_id;

DECLARE @inventory_children TABLE (
    module_name varchar(50),
    module_key varchar(50),
    description varchar(200),
    icon varchar(50),
    route_url varchar(100),
    display_order int
);

INSERT INTO @inventory_children (
    module_name,
    module_key,
    description,
    icon,
    route_url,
    display_order
)
VALUES
    ('Inventory Overview', 'inventory-overview', 'Inventory overview and stock summary', 'inventory_2', '/inventory', 1),
    ('Inventory Entries', 'inventory-entries', 'Inventory stock entries', 'add_box', '/inventory/entries', 2),
    ('Inventory Outputs', 'inventory-outputs', 'Inventory stock outputs', 'outbox', '/inventory/outputs', 3),
    ('Inventory Adjustments', 'inventory-adjustments', 'Inventory stock adjustments', 'tune', '/inventory/adjustments', 4),
    ('Inventory Movements', 'inventory-movements', 'Inventory movement history', 'sync_alt', '/inventory/movements', 5),
    ('Inventory Warehouses', 'inventory-warehouses', 'Inventory warehouse management', 'warehouse', '/inventory/warehouses', 6);

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
SELECT
    child.module_name,
    child.module_key,
    child.description,
    child.icon,
    child.route_url,
    child.display_order,
    1,
    @inventory_module_id,
    @now
FROM @inventory_children child
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.modules existing
    WHERE existing.module_key = child.module_key
);

UPDATE existing
SET existing.parent_module_id = @inventory_module_id,
    existing.icon = child.icon,
    existing.route_url = child.route_url,
    existing.display_order = child.display_order,
    existing.is_active = 1
FROM dbo.modules existing
INNER JOIN @inventory_children child
    ON child.module_key = existing.module_key;

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
SELECT
    parent_permissions.role_id,
    child_modules.module_id,
    parent_permissions.can_view,
    parent_permissions.can_create,
    parent_permissions.can_edit,
    parent_permissions.can_delete,
    parent_permissions.can_export,
    parent_permissions.admin_actions,
    parent_permissions.other_actions,
    SYSUTCDATETIME()
FROM dbo.role_modules parent_permissions
INNER JOIN dbo.modules child_modules
    ON child_modules.parent_module_id = @inventory_module_id
WHERE parent_permissions.module_id = @inventory_module_id
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.role_modules existing
      WHERE existing.role_id = parent_permissions.role_id
        AND existing.module_id = child_modules.module_id
  );
