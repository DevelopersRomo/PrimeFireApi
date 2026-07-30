import pytest

from models.hardware_inventory import HardwareInventory


@pytest.fixture(autouse=True)
def _grant_hardware_mutations(permission_override) -> None:
    permission_override("hardware", {"can_create", "can_edit", "can_delete"})


def test_hardware_search_status_and_total(client, auth_headers, db_session):
    db_session.add(HardwareInventory(serial_number="NEEDLE-1", brand="Acme", status="Active"))
    db_session.add(HardwareInventory(serial_number="OTHER-1", brand="Acme", status="Retired"))
    db_session.commit()

    response = client.get("/hardware?with_meta=true&search=NEEDLE&status=active", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["serial_number"] == "NEEDLE-1"
