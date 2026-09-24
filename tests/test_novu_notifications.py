import hashlib
import hmac
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from core.config import settings
from models.employees import Employees
from services.notifications import novu

SECRET = "test-novu-secret"


def test_subscriber_id_is_scoped_by_database_route():
    assert novu.subscriber_id("primefire", 42) == "primefire:42"
    assert novu.subscriber_id("clienta", 42) != novu.subscriber_id("primefire", 42)


def test_subscriber_hash_matches_novu_hmac_spec(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", SECRET)
    expected = hmac.new(SECRET.encode(), b"primefire:42", hashlib.sha256).hexdigest()

    assert novu.subscriber_hash("primefire:42") == expected


def test_trigger_is_a_noop_when_novu_is_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "")
    with patch("services.notifications.novu.Novu") as client_cls:
        assert novu.trigger("ticket-closed", "main", [novu.Recipient(1, "a@x.com", None)], {}, "t-1") is False

    client_cls.assert_not_called()


def test_trigger_sends_one_event_per_recipient_with_idempotent_transaction(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", SECRET)
    client = MagicMock()
    recipients = [
        novu.Recipient(1, "a@x.com", "Ana"),
        novu.Recipient(2, "b@x.com", "Luis"),
    ]
    with patch("services.notifications.novu.Novu") as client_cls:
        client_cls.return_value.__enter__.return_value = client
        assert novu.trigger("ticket-closed", "main", recipients, {"ticket_id": 5}, "ticket-5-closed") is True

    requests = [call.kwargs["trigger_event_request_dto"] for call in client.trigger.call_args_list]
    assert [r.to.subscriber_id for r in requests] == ["main:1", "main:2"]
    assert [r.transaction_id for r in requests] == ["ticket-5-closed:main:1", "ticket-5-closed:main:2"]
    assert all(r.workflow_id == "ticket-closed" and r.payload == {"ticket_id": 5} for r in requests)


def test_trigger_never_raises_when_novu_fails(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", SECRET)
    with patch("services.notifications.novu.Novu") as client_cls:
        client_cls.return_value.__enter__.return_value.trigger.side_effect = RuntimeError("novu down")
        assert novu.trigger("ticket-closed", "main", [novu.Recipient(1, "a@x.com", None)], {}, "t-1") is False


def test_inbox_config_is_disabled_without_novu(client: TestClient, auth_headers: dict, auth_overrides, monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "")

    response = client.get("/notifications/inbox", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"enabled": False}


def test_inbox_config_returns_signed_subscriber(
    client: TestClient, auth_headers: dict, current_employee: Employees, auth_overrides, monkeypatch
):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", SECRET)
    monkeypatch.setattr(settings, "NOVU_APPLICATION_IDENTIFIER", "app-id")

    data = client.get("/notifications/inbox", headers=auth_headers).json()

    assert data["enabled"] is True
    assert data["application_identifier"] == "app-id"
    assert data["subscriber_id"].endswith(f":{current_employee.employee_id}")
    assert data["subscriber_hash"] == novu.subscriber_hash(data["subscriber_id"])


def test_db_route_normalizes_tenant_keys_that_point_to_the_main_database():
    """A tenant whose key is "MAIN" uses the main DB (ConnectionManager treats it case-insensitively),
    so it must share the "main" route or its users get a different Novu subscriber than the SLA job."""
    from bd import dependencies

    request = MagicMock()
    with patch.object(dependencies, "_get_token_route", return_value=("MAIN", False, None)):
        assert dependencies.get_db_route(request) == "main"
    with patch.object(dependencies, "_get_token_route", return_value=("clienta", False, None)):
        assert dependencies.get_db_route(request) == "clienta"
