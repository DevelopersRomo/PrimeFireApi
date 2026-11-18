from datetime import date, timedelta
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from sqlmodel import Session, select

from api import timesheet
from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from main import app
from models.countries import Countries
from models.employees import Employees
from models.time_off import Holiday
from models.timesheet import TimeSheetPunch, TimeSheetPunchStatusEnum
from services.holidays import holiday_country_filter

HOLIDAY_DAY = "2030-03-04"


def _days(n: int) -> str:
    return (date.today() + timedelta(days=n)).strftime("%Y-%m-%d")  # noqa: DTZ011


@pytest.fixture
def countries(db_session: Session) -> tuple[Countries, Countries]:
    mexico = Countries(name="Mexico")
    colombia = Countries(name="Colombia")
    db_session.add(mexico)
    db_session.add(colombia)
    db_session.commit()
    db_session.refresh(mexico)
    db_session.refresh(colombia)
    return mexico, colombia


@pytest.fixture
def mx_employee(db_session: Session, countries) -> Employees:
    emp = Employees(email="mx@example.com", first_name="Mex", last_name="Ican", country_id=countries[0].country_id)
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def co_employee(db_session: Session, countries) -> Employees:
    emp = Employees(email="co@example.com", first_name="Colom", last_name="Bian", country_id=countries[1].country_id)
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def same_day_holidays(db_session: Session, countries) -> None:
    mexico, colombia = countries
    db_session.add(Holiday(name="Global Day", date="2030-01-01", year=2030))
    db_session.add(Holiday(name="Mexico Day", date=HOLIDAY_DAY, year=2030, country_id=mexico.country_id))
    db_session.add(Holiday(name="Colombia Day", date="2030-03-05", year=2030, country_id=colombia.country_id))
    db_session.commit()


@pytest.fixture
def act_as():
    def _act(employee: Employees, permissions: list | None = None):
        perms = {"permissions": permissions or []}
        app.dependency_overrides[get_current_employee] = lambda: employee
        app.dependency_overrides[get_current_employee_with_permissions] = lambda: perms
        app.dependency_overrides[require_authentication] = lambda: {"sub": employee.email}

    yield _act
    app.dependency_overrides.pop(get_current_employee, None)
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)
    app.dependency_overrides.pop(require_authentication, None)


def _holiday_perms(*actions: str) -> list:
    return [{"module_key": "holidays", "permissions": dict.fromkeys(actions, True)}]


# --- shared country filter -------------------------------------------------


def test_filter_returns_global_and_own_country(db_session: Session, countries, same_day_holidays):
    names = {h.name for h in db_session.exec(select(Holiday).where(holiday_country_filter(countries[0].country_id)))}
    assert names == {"Global Day", "Mexico Day"}


def test_filter_without_country_returns_only_global(db_session: Session, same_day_holidays):
    names = {h.name for h in db_session.exec(select(Holiday).where(holiday_country_filter(None)))}
    assert names == {"Global Day"}


def test_filter_accepts_several_countries(db_session: Session, countries, same_day_holidays):
    query = select(Holiday).where(holiday_country_filter(countries[0].country_id, countries[1].country_id))
    assert len(db_session.exec(query).all()) == 3


# --- calendar --------------------------------------------------------------


def test_calendar_hides_other_country_holidays(act_as, client: TestClient, mx_employee, same_day_holidays):
    act_as(mx_employee)
    response = client.get("/api/v1/calendar")
    assert response.status_code == 200
    titles = {e["title"] for e in response.json() if e["type"] == "holiday"}
    assert titles == {"Global Day", "Mexico Day"}


def test_calendar_includes_countries_of_visible_reports(
    act_as, client: TestClient, db_session: Session, mx_employee, co_employee, same_day_holidays
):
    co_employee.manager_employee_id = mx_employee.employee_id
    db_session.add(co_employee)
    db_session.commit()

    act_as(mx_employee)
    titles = {e["title"] for e in client.get("/api/v1/calendar").json() if e["type"] == "holiday"}
    assert titles == {"Global Day", "Mexico Day", "Colombia Day"}


# --- upcoming --------------------------------------------------------------


def test_upcoming_returns_future_global_and_own_country_ordered(
    act_as, client: TestClient, db_session: Session, mx_employee, countries
):
    mexico, colombia = countries
    db_session.add(Holiday(name="Past", date=_days(-1), year=2030))
    db_session.add(Holiday(name="Later", date=_days(20), year=2030))
    db_session.add(Holiday(name="Today", date=_days(0), year=2030, country_id=mexico.country_id))
    db_session.add(Holiday(name="Soon", date=_days(5), year=2030))
    db_session.add(Holiday(name="Other country", date=_days(1), year=2030, country_id=colombia.country_id))
    db_session.commit()

    act_as(mx_employee)
    response = client.get("/api/v1/holidays/upcoming?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert [h["name"] for h in data] == ["Today", "Soon"]
    assert data[0]["country_name"] == "Mexico"
    assert data[1]["country_id"] is None


def test_upcoming_without_country_returns_only_global(act_as, client: TestClient, db_session: Session, countries):
    nowhere = Employees(email="nowhere@example.com")
    db_session.add(nowhere)
    db_session.add(Holiday(name="Global", date=_days(3), year=2030))
    db_session.add(Holiday(name="MX", date=_days(2), year=2030, country_id=countries[0].country_id))
    db_session.commit()
    db_session.refresh(nowhere)

    act_as(nowhere)
    assert [h["name"] for h in client.get("/api/v1/holidays/upcoming").json()] == ["Global"]


# --- list ------------------------------------------------------------------


def test_list_filters_by_country_year_and_search(act_as, client: TestClient, mx_employee, countries, same_day_holidays):
    act_as(mx_employee)
    mexico = countries[0]

    data = client.get(f"/api/v1/holidays?country_id={mexico.country_id}").json()
    assert {h["name"] for h in data} == {"Global Day", "Mexico Day"}

    data = client.get(f"/api/v1/holidays?country_id={mexico.country_id}&only_country=true").json()
    assert [h["name"] for h in data] == ["Mexico Day"]

    data = client.get("/api/v1/holidays?search=colombia&year=2030&with_meta=true").json()
    assert data["total"] == 1
    assert data["items"][0]["country_name"] == "Colombia"


# --- CRUD ------------------------------------------------------------------


def test_crud_requires_holidays_permission(act_as, client: TestClient, mx_employee, same_day_holidays, db_session):
    act_as(mx_employee, [{"module_key": "timeoff", "permissions": {"can_create": True}}])
    holiday_id = db_session.exec(select(Holiday)).first().holiday_id

    assert client.post("/api/v1/holidays", json={"name": "X", "date": "2030-06-01"}).status_code == 403
    assert client.put(f"/api/v1/holidays/{holiday_id}", json={"name": "X", "date": "2030-06-01"}).status_code == 403
    assert client.delete(f"/api/v1/holidays/{holiday_id}").status_code == 403


def test_create_update_delete_holiday(act_as, client: TestClient, db_session: Session, mx_employee, countries):
    act_as(mx_employee, _holiday_perms("can_view", "can_create", "can_edit", "can_delete"))
    mexico = countries[0]

    response = client.post(
        "/api/v1/holidays", json={"name": "  Independence  ", "date": "2031-09-16", "country_id": mexico.country_id}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Independence"
    assert created["year"] == 2031
    assert created["country_name"] == "Mexico"

    response = client.put(
        f"/api/v1/holidays/{created['holiday_id']}", json={"name": "Grito", "date": "2032-09-16", "country_id": None}
    )
    assert response.status_code == 200
    assert response.json()["year"] == 2032
    assert response.json()["country_id"] is None

    assert client.delete(f"/api/v1/holidays/{created['holiday_id']}").status_code == 204
    assert db_session.exec(select(Holiday)).all() == []
    assert client.delete(f"/api/v1/holidays/{created['holiday_id']}").status_code == 404


def test_create_duplicate_is_conflict(act_as, client: TestClient, mx_employee, countries, same_day_holidays):
    act_as(mx_employee, _holiday_perms("can_create"))
    mexico, colombia = countries

    payload = {"name": "Again", "date": HOLIDAY_DAY, "country_id": mexico.country_id}
    assert client.post("/api/v1/holidays", json=payload).status_code == 409
    # Same date in another country is a different holiday.
    payload["country_id"] = colombia.country_id
    assert client.post("/api/v1/holidays", json=payload).status_code == 201
    # Two global holidays on the same date are duplicates too.
    assert client.post("/api/v1/holidays", json={"name": "G", "date": "2030-01-01"}).status_code == 409


def test_update_into_duplicate_is_conflict(
    act_as, client: TestClient, db_session: Session, mx_employee, countries, same_day_holidays
):
    act_as(mx_employee, _holiday_perms("can_edit"))
    global_day = db_session.exec(select(Holiday).where(Holiday.name == "Global Day")).one()
    payload = {"name": "Moved", "date": HOLIDAY_DAY, "country_id": countries[0].country_id}
    assert client.put(f"/api/v1/holidays/{global_day.holiday_id}", json=payload).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Bad", "date": "2030-13-01"},
        {"name": "Bad", "date": "01/02/2030"},
        {"name": "   ", "date": "2030-02-01"},
        {"name": "x" * 101, "date": "2030-02-01"},
        {"name": "Ghost", "date": "2030-02-01", "country_id": 9999},
    ],
)
def test_create_rejects_invalid_payload(act_as, client: TestClient, mx_employee, payload):
    act_as(mx_employee, _holiday_perms("can_create"))
    assert client.post("/api/v1/holidays", json=payload).status_code == 422


# --- timesheet -------------------------------------------------------------


def test_time_off_maps_use_employee_country(db_session: Session, mx_employee, co_employee, same_day_holidays):
    day = date(2030, 3, 4)
    mx_totals, _ = timesheet._get_time_off_maps(db_session, mx_employee.employee_id, day, day)  # noqa: SLF001
    co_totals, _ = timesheet._get_time_off_maps(db_session, co_employee.employee_id, day, day)  # noqa: SLF001
    assert mx_totals[day]["holiday"] > 0
    assert day not in co_totals


def _punch(db_session: Session, employee: Employees) -> None:
    db_session.add(
        TimeSheetPunch(
            employee_id=employee.employee_id,
            customer_id=1,
            status=TimeSheetPunchStatusEnum.CLOSED.value,
            clock_in_at=f"{HOLIDAY_DAY} 14:00:00",
            clock_out_at=f"{HOLIDAY_DAY} 18:00:00",
            worked_minutes=240,
            created_at=f"{HOLIDAY_DAY} 14:00:00",
            updated_at=f"{HOLIDAY_DAY} 18:00:00",
        )
    )
    db_session.commit()


def _holiday_column_by_first_cell(content: bytes) -> dict[str, str]:
    rows = list(load_workbook(BytesIO(content)).active.iter_rows(values_only=True))
    header = rows[0]
    return {row[0]: row[header.index("holiday")] for row in rows[1:]}


TIMESHEET_ADMIN = [{"module_key": "timesheet", "permissions": {"admin_actions": True}}]


def test_admin_export_resolves_holidays_per_employee_country(
    act_as, client: TestClient, db_session: Session, mx_employee, co_employee, same_day_holidays
):
    _punch(db_session, mx_employee)
    _punch(db_session, co_employee)
    act_as(mx_employee, TIMESHEET_ADMIN)

    response = client.get(f"/api/v1/timesheet/admin/export?start_date={HOLIDAY_DAY}&end_date={HOLIDAY_DAY}")
    assert response.status_code == 200
    assert _holiday_column_by_first_cell(response.content) == {"Mex Ican": "true", "Colom Bian": "false"}


@pytest.mark.parametrize(("employee_fixture", "expected"), [("mx_employee", "true"), ("co_employee", "false")])
def test_employee_export_uses_target_employee_country(
    act_as, client: TestClient, db_session: Session, mx_employee, same_day_holidays, request, employee_fixture, expected
):
    target = request.getfixturevalue(employee_fixture)
    _punch(db_session, target)
    act_as(mx_employee, TIMESHEET_ADMIN)

    response = client.get(
        f"/api/v1/timesheet/export?start_date={HOLIDAY_DAY}&end_date={HOLIDAY_DAY}&employee_id={target.employee_id}"
    )
    assert response.status_code == 200
    assert _holiday_column_by_first_cell(response.content) == {HOLIDAY_DAY: expected}
