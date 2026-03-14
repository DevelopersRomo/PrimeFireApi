from fastapi.testclient import TestClient


def test_customers_crud(client: TestClient, auth_headers: dict):
    response = client.get("/customers/")
    assert response.status_code in {401, 200}

    response = client.get("/customers/", headers=auth_headers)
    assert response.status_code == 200
