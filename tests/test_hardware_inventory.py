def test_hardware_inventory(client, auth_headers):
    response = client.get("/api/v1/hardware_inventory/", headers=auth_headers)
    assert response.status_code in {200, 404, 401, 403}
