import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/inventory/warehouse-locations",
        "/inventory/warehouses",
        "/inventory/movements",
        "/inventory/movement-approvals",
        "/inventory/stock",
        "/inventory/stock-metrics",
        "/inventory/stock-facets",
        "/inventory/warehouses/1",
        "/inventory/movements/1",
        "/inventory/stock/1",
    ],
)
def test_inventory_reads_require_inventory_can_view(client, auth_headers, permission_override, path):
    permission_override("inventory", set())

    response = client.get(path, headers=auth_headers)

    assert response.status_code == 403
