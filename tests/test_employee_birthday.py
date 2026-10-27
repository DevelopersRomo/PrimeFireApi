from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from core.microsoft_graph import parse_graph_birthday
from models.employees import Employees


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("", None),
        ("0001-01-01T00:00:00Z", None),
        ("1990-05-14T00:00:00Z", "05-14"),
        ("2000-05-13T22:00:00Z", "05-14"),
        ("2000-05-14T05:00:00Z", "05-14"),
        ("2000-12-31T23:00:00Z", "01-01"),
    ],
)
def test_parse_graph_birthday(value, expected) -> None:
    assert parse_graph_birthday(value) == expected


def test_me_birthday_returns_graph_value(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
) -> None:
    current_employee.azure_oid = "oid-123"
    db_session.commit()

    with patch("api.employees.graph_client") as mock_graph:
        mock_graph.get_user_birthday = AsyncMock(return_value="05-14")
        response = client.get("/employees/me/birthday", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"birthday": "05-14", "decorations_preview": False}
    mock_graph.get_user_birthday.assert_awaited_once_with("oid-123")


def test_me_birthday_is_null_without_azure_oid(
    client: TestClient, auth_headers: dict, current_employee: Employees, auth_overrides
) -> None:
    assert current_employee.azure_oid is None

    with patch("api.employees.graph_client") as mock_graph:
        mock_graph.get_user_birthday = AsyncMock(return_value="05-14")
        response = client.get("/employees/me/birthday", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"birthday": None, "decorations_preview": False}
    mock_graph.get_user_birthday.assert_not_called()


def test_me_birthday_is_null_when_graph_fails(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
) -> None:
    current_employee.azure_oid = "oid-123"
    db_session.commit()

    with patch("api.employees.graph_client") as mock_graph:
        mock_graph.get_user_birthday = AsyncMock(side_effect=RuntimeError("Graph unavailable"))
        response = client.get("/employees/me/birthday", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"birthday": None, "decorations_preview": False}


def test_me_birthday_exposes_decorations_preview_flag(
    client: TestClient, auth_headers: dict, current_employee: Employees, auth_overrides
) -> None:
    with patch("api.employees.settings.DECORATIONS_PREVIEW", True):
        response = client.get("/employees/me/birthday", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"birthday": None, "decorations_preview": True}
