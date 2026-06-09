def test_inventory_warehouse_location_crud(client, auth_headers):
    create_response = client.post(
        "/inventory/warehouse-locations",
        headers=auth_headers,
        json={"name": "Warehouse 1"},
    )

    assert create_response.status_code == 200, create_response.text
    created_location = create_response.json()
    location_id = created_location["warehouse_location_id"]
    assert created_location["name"] == "Warehouse 1"

    list_response = client.get(
        "/inventory/warehouse-locations?search=warehouse",
        headers=auth_headers,
    )
    assert list_response.status_code == 200, list_response.text
    assert any(item["warehouse_location_id"] == location_id for item in list_response.json())

    duplicate_response = client.post(
        "/inventory/warehouse-locations",
        headers=auth_headers,
        json={"name": "Warehouse 1"},
    )
    assert duplicate_response.status_code == 400, duplicate_response.text


def test_inventory_warehouse_crud(client, auth_headers):
    location_response = client.post(
        "/inventory/warehouse-locations",
        headers=auth_headers,
        json={"name": "Plant 1"},
    )
    assert location_response.status_code == 200, location_response.text
    location_id = location_response.json()["warehouse_location_id"]

    create_response = client.post(
        "/inventory/warehouses",
        headers=auth_headers,
        json={"name": "Main Warehouse", "location_id": location_id},
    )

    assert create_response.status_code == 200, create_response.text
    created = create_response.json()
    warehouse_id = created["warehouse_id"]
    assert created["location_id"] == location_id
    assert created["location"] == "Plant 1"

    list_response = client.get("/inventory/warehouses", headers=auth_headers)
    assert list_response.status_code == 200, list_response.text
    assert any(item["warehouse_id"] == warehouse_id for item in list_response.json())

    update_response = client.patch(
        f"/inventory/warehouses/{warehouse_id}",
        headers=auth_headers,
        json={"location": "Plant 2", "is_active": False},
    )

    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["location"] == "Plant 2"
    assert updated["is_active"] is False

    delete_response = client.delete(
        f"/inventory/warehouses/{warehouse_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["message"] == "Warehouse deleted successfully"
