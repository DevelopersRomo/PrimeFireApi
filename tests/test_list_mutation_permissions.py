import pytest

MUTATION_CASES = [
    (
        "products",
        "can_create",
        "POST",
        "/products",
        {"name": "Permission Product", "type": "Product"},
    ),
    ("products", "can_edit", "PATCH", "/products/999999", {"name": "Updated"}),
    ("products", "can_delete", "DELETE", "/products/999999", None),
    (
        "licenses",
        "can_create",
        "POST",
        "/licenses",
        {
            "software": "Permission License",
            "version": "1.0",
            "key": "PERMISSION-KEY",
            "account": "permission@example.com",
            "password": "secret",
            "employee_id": 1,
        },
    ),
    ("licenses", "can_edit", "PATCH", "/licenses/999999", {"software": "Updated"}),
    ("licenses", "can_delete", "DELETE", "/licenses/999999", None),
    (
        "hardware",
        "can_create",
        "POST",
        "/hardware",
        {"serial_number": "PERMISSION-HARDWARE", "brand": "Acme"},
    ),
    (
        "hardware",
        "can_edit",
        "PUT",
        "/hardware/999999",
        {"serial_number": "MISSING-HARDWARE", "brand": "Acme"},
    ),
    ("hardware", "can_delete", "DELETE", "/hardware/999999", None),
    (
        "jobs",
        "can_create",
        "POST",
        "/jobs",
        {"title": "Permission Job", "status": "active", "employee_id": 1},
    ),
    ("jobs", "can_edit", "PUT", "/jobs/999999", {"title": "Updated"}),
    ("jobs", "can_delete", "DELETE", "/jobs/999999", None),
    (
        "quotations",
        "can_create",
        "POST",
        "/quotations/",
        {
            "customer_id": 999999,
            "quote_date": "2026-07-29T00:00:00Z",
            "status": "Draft",
        },
    ),
    ("quotations", "can_edit", "PATCH", "/quotations/999999", {"status": "Approved"}),
    ("quotations", "can_delete", "DELETE", "/quotations/999999", None),
    (
        "inventory",
        "can_create",
        "POST",
        "/inventory/warehouses",
        {"name": "Permission Warehouse"},
    ),
    ("inventory", "can_edit", "PATCH", "/inventory/warehouses/999999", {"name": "Updated"}),
    ("inventory", "can_delete", "DELETE", "/inventory/warehouses/999999", None),
    (
        "inventory",
        "can_create",
        "POST",
        "/inventory/entries",
        {"product_id": 999999, "movement_type": "IN", "quantity": 1},
    ),
]


@pytest.mark.parametrize(("module_key", "action", "method", "path", "payload"), MUTATION_CASES)
def test_mutations_require_exact_module_permission(
    client, auth_headers, permission_override, module_key, action, method, path, payload
) -> None:
    permission_override(module_key, set())
    denied = client.request(method, path, headers=auth_headers, json=payload)

    assert denied.status_code == 403
    assert denied.json()["detail"] == f"Missing '{action}' permission for module '{module_key}'."

    permission_override(module_key, {action})
    allowed = client.request(method, path, headers=auth_headers, json=payload)

    assert allowed.status_code != 403


def test_job_list_remains_public(client, permission_override) -> None:
    permission_override("jobs", set())

    response = client.get("/jobs")

    assert response.status_code == 200
