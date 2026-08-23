from datetime import date

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from api.expenses import create_report, list_reports, update_report
from models.employees import Employees
from models.expenses import ExpenseReports
from schemas.expenses import ExpenseReportCreate, ExpenseReportUpdate


def _employee(db: Session) -> Employees:
    employee = Employees(first_name="Date", last_name="Tester", display_name="Date Tester", email="date@test.local")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def test_create_rejects_inverted_trip_date_range(db_session: Session):
    employee = _employee(db_session)

    with pytest.raises(HTTPException) as error:
        create_report(
            ExpenseReportCreate(title="Trip", trip_start_date=date(2026, 8, 12), trip_end_date=date(2026, 8, 10)),
            db_session,
            employee,
            {},
        )

    assert error.value.status_code == 422


def test_update_rejects_inverted_trip_date_range_in_either_field_order(db_session: Session):
    employee = _employee(db_session)
    report = ExpenseReports(
        folio="VIA-2026-0001",
        employee_id=employee.employee_id,
        title="Trip",
        trip_start_date=date(2026, 8, 10),
        trip_end_date=date(2026, 8, 12),
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    for payload in (
        ExpenseReportUpdate(trip_start_date=date(2026, 8, 13)),
        ExpenseReportUpdate(trip_end_date=date(2026, 8, 9)),
    ):
        with pytest.raises(HTTPException) as error:
            update_report(report.report_id, payload, db_session, employee, {})
        assert error.value.status_code == 422


def test_list_rejects_inverted_filter_range_and_accepts_equal_limits(db_session: Session):
    employee = _employee(db_session)

    with pytest.raises(HTTPException) as error:
        list_reports(
            employee_id=None,
            job_id=None,
            report_status=None,
            date_from=date(2026, 8, 12),
            date_to=date(2026, 8, 10),
            search=None,
            mine_only=False,
            pending_for_me=False,
            skip=0,
            limit=25,
            db=db_session,
            current_employee=employee,
            user_permissions={},
        )
    assert error.value.status_code == 422

    response = list_reports(
        employee_id=None,
        job_id=None,
        report_status=None,
        date_from=date(2026, 8, 10),
        date_to=date(2026, 8, 10),
        search=None,
        mine_only=False,
        pending_for_me=False,
        skip=0,
        limit=25,
        db=db_session,
        current_employee=employee,
        user_permissions={},
    )
    assert response.total == 0


def test_create_accepts_equal_trip_date_limits(db_session: Session):
    employee = _employee(db_session)

    report = create_report(
        ExpenseReportCreate(title="Trip", trip_start_date=date(2026, 8, 10), trip_end_date=date(2026, 8, 10)),
        db_session,
        employee,
        {},
    )

    assert report.trip_start_date == report.trip_end_date
