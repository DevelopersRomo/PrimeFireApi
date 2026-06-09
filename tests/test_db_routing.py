from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException

import bd.dependencies as db_dependencies


class DummySession:
    def __init__(self, name: str):
        self.name = name
        self.closed = False

    def close(self):
        self.closed = True


def _azure_headers(email: str) -> dict[str, str]:
    token = jwt.encode(
        {
            "oid": "azure-user-id",
            "preferred_username": email,
        },
        key="test",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_get_db_routes_primefire_microsoft_users_to_primefire_db(monkeypatch):
    sessions = {}

    def primefire_session_factory():
        sessions["primefire"] = DummySession("primefire")
        return sessions["primefire"]

    def main_session_factory():
        sessions["main"] = DummySession("main")
        return sessions["main"]

    monkeypatch.setattr(db_dependencies, "SessionPrimeFire", primefire_session_factory)
    monkeypatch.setattr(db_dependencies, "SessionLocal", main_session_factory)

    request = SimpleNamespace(headers=_azure_headers("user@primefire.us"))
    generator = db_dependencies.get_db(request)

    db = next(generator)
    assert db.name == "primefire"
    assert "main" not in sessions

    with pytest.raises(StopIteration):
        next(generator)
    assert sessions["primefire"].closed is True


def test_get_db_rejects_non_primefire_microsoft_users(monkeypatch):
    monkeypatch.setattr(db_dependencies, "SessionPrimeFire", lambda: DummySession("primefire"))
    monkeypatch.setattr(db_dependencies, "SessionLocal", lambda: DummySession("main"))

    request = SimpleNamespace(headers=_azure_headers("user@example.com"))

    with pytest.raises(HTTPException) as exc:
        next(db_dependencies.get_db(request))

    assert exc.value.status_code == 403


def test_get_db_does_not_fallback_when_primefire_db_is_missing(monkeypatch):
    monkeypatch.setattr(db_dependencies, "SessionPrimeFire", None)
    monkeypatch.setattr(db_dependencies, "SessionLocal", lambda: DummySession("main"))

    request = SimpleNamespace(headers=_azure_headers("user@primefire.do"))

    with pytest.raises(HTTPException) as exc:
        next(db_dependencies.get_db(request))

    assert exc.value.status_code == 500
    assert "PRIMEFIRE_DB_SERVER" in exc.value.detail
