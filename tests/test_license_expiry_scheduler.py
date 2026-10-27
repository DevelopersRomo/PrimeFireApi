from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import Session, select

from core import license_expiry_scheduler as job
from core.config import settings
from core.mail_profiles import DEFAULT_MAIL_PROFILE
from models.employees import EmployeeRoles, Employees, Roles
from models.licenses import Licenses
from models.modules import Modules, RoleModules
from models.tenants import Tenants
from tests.conftest import create_test_record

TODAY = date(2026, 10, 26)


@pytest.fixture
def novu_enabled(monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "test-secret")


@pytest.fixture
def send_email():
    with patch("core.license_expiry_scheduler.send_outlook_email", new_callable=AsyncMock) as send:
        send.return_value = (True, "id", None)
        yield send


def _grant(db: Session, employee: Employees, module_key: str = "licenses", can_view: bool = True) -> None:
    role = create_test_record(db, Roles, role_name=f"Role {employee.employee_id} {module_key}")
    module = db.exec(select(Modules).where(Modules.module_key == module_key)).first() or create_test_record(
        db, Modules, module_name=module_key, module_key=module_key
    )
    create_test_record(db, RoleModules, role_id=role.role_id, module_id=module.module_id, can_view=can_view)
    create_test_record(db, EmployeeRoles, employee_id=employee.employee_id, role_id=role.role_id)
    db.commit()


def _license(db: Session, **overrides) -> Licenses:
    values = {
        "software": "AutoCAD",
        "version": "2025",
        "expiry_date": TODAY - timedelta(days=1),
        "account": "cad@example.com",
        "key": "SECRET-KEY-123",
        "password": "hunter2-pass",
        "notes": "private-note",
    }
    values.update(overrides)
    lic = create_test_record(db, Licenses, **values)
    db.commit()
    return lic


def test_only_licenses_expired_before_today_are_selected(db_session: Session):
    expired = _license(db_session)
    _license(db_session, software="Today", expiry_date=TODAY)
    _license(db_session, software="Future", expiry_date=TODAY + timedelta(days=3))
    _license(db_session, software="No date", expiry_date=None)

    assert [lic.license_id for lic in job.find_expired_licenses(db_session, TODAY)] == [expired.license_id]


def test_recipients_are_employees_whose_roles_can_view_licenses(
    db_session: Session, current_employee: Employees, other_employee: Employees
):
    _grant(db_session, current_employee)
    _grant(db_session, current_employee)  # second role with the same access: still one recipient
    _grant(db_session, other_employee, module_key="tickets")  # other module only
    no_view = create_test_record(db_session, Employees, email="noview@example.com", display_name="No View")
    no_email = create_test_record(db_session, Employees, email="", display_name="No Email")
    db_session.commit()
    _grant(db_session, no_view, can_view=False)
    _grant(db_session, no_email)

    assert [e.employee_id for e in job.find_recipients(db_session)] == [current_employee.employee_id]


def test_digest_goes_by_email_and_novu_without_secrets(
    db_session: Session, current_employee: Employees, other_employee: Employees, novu_enabled, send_email
):
    _grant(db_session, current_employee)
    _license(db_session, employee_id=other_employee.employee_id, software="<b>Evil</b>")

    with patch("core.license_expiry_scheduler.novu.trigger", return_value=True) as trigger:
        assert job.send_license_digests(db_session, "clienta", TODAY, "clienta_tenant") == 1

    email = send_email.call_args.kwargs
    assert email["to_emails"] == ["test@example.com"]
    assert email["mail_profile"] == "clienta_tenant"
    body = email["body"]
    assert "&lt;b&gt;Evil&lt;/b&gt;" in body and "<b>Evil</b>" not in body
    assert "Other User" in body and "cad@example.com" in body and "2026-10-25" in body
    assert f"{settings.APP_URL}/licenses" in body

    workflow_id, db_route, recipients, payload, transaction_id = trigger.call_args.args
    assert (workflow_id, db_route) == ("license-expired-digest", "clienta")
    assert [r.employee_id for r in recipients] == [current_employee.employee_id]
    assert payload == {"count": 1, "url": f"{settings.APP_URL}/licenses"}
    assert transaction_id == f"license-expired-digest-clienta-{current_employee.employee_id}-2026-10-26"

    for secret in ("SECRET-KEY-123", "hunter2-pass", "private-note"):
        assert secret not in body and secret not in str(payload)


def test_nothing_is_sent_without_expired_licenses(db_session: Session, current_employee: Employees, send_email):
    _grant(db_session, current_employee)
    _license(db_session, expiry_date=TODAY)

    assert job.send_license_digests(db_session, "main", TODAY, DEFAULT_MAIL_PROFILE) == 0
    send_email.assert_not_called()


def test_novu_is_skipped_when_not_configured(db_session: Session, current_employee: Employees, monkeypatch, send_email):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "")
    _grant(db_session, current_employee)
    _license(db_session)

    with patch("core.license_expiry_scheduler.novu.trigger") as trigger:
        assert job.send_license_digests(db_session, "main", TODAY, DEFAULT_MAIL_PROFILE) == 1

    trigger.assert_not_called()
    send_email.assert_called_once()


def test_one_failing_email_does_not_stop_the_others(
    db_session: Session, current_employee: Employees, other_employee: Employees, send_email
):
    _grant(db_session, current_employee)
    _grant(db_session, other_employee)
    _license(db_session)
    send_email.side_effect = [RuntimeError("graph down"), (True, "id", None)]

    assert job.send_license_digests(db_session, "main", TODAY, DEFAULT_MAIL_PROFILE) == 1
    assert send_email.call_count == 2


def test_mail_profile_comes_from_the_tenant_matching_the_route(db_session: Session):
    create_test_record(db_session, Tenants, name="A", db_connection_key="ClientA", mail_profile="clienta_tenant")
    create_test_record(db_session, Tenants, name="Main", db_connection_key="MAIN", mail_profile="main_tenant")
    db_session.commit()

    assert job.mail_profile_for(db_session, "clienta") == "clienta_tenant"
    assert job.mail_profile_for(db_session, "main") == "main_tenant"
    assert job.mail_profile_for(db_session, "unknown") == DEFAULT_MAIL_PROFILE


@pytest.mark.parametrize(
    ("now", "seconds"),
    [
        (datetime(2026, 10, 26, 12, 30), 30 * 60),  # noqa: DTZ001 - before the hour: today
        (datetime(2026, 10, 26, 13, 0), 24 * 3600),  # noqa: DTZ001 - exactly at it: tomorrow, no double run
        (datetime(2026, 10, 26, 14, 0), 23 * 3600),  # noqa: DTZ001 - after it: tomorrow
    ],
)
def test_seconds_until_next_run(now, seconds):
    assert job.seconds_until_next_run(now, 13) == seconds
