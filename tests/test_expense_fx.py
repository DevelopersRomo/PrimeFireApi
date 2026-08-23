"""Foreign-currency lines must be restated in the base currency before judging.

`amount_base` feeds the report total, the band that selects the approval chain,
and the category caps. A line left at rate 1 routes and caps against a number
that is not money, so these cases pin both the happy path and the refusal to
invent a rate when the feed cannot answer.
"""

from datetime import date
from decimal import Decimal

import httpx
import pytest
from sqlmodel import Session, select

from api.expenses import create_item, update_item
from models.employees import Employees
from models.expenses import ExpenseReportFlags, ExpenseReportItems, ExpenseReports
from schemas.expenses import ExpenseItemCreate, ExpenseItemUpdate
from services.expenses import fx, policies

PLAIN_PERMISSIONS = {"permissions": [{"module_key": "expenses", "permissions": {"admin_actions": False}}]}


@pytest.fixture(autouse=True)
def _no_memoised_rates():
    fx.clear_cache()
    yield
    fx.clear_cache()


def _employee(db: Session, name: str) -> Employees:
    employee = Employees(first_name=name, last_name="Test", display_name=name, email=f"{name}@primefire.us")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _report(db: Session, employee: Employees, suffix: int) -> ExpenseReports:
    report = ExpenseReports(
        folio=f"VIA-2026-{suffix:04d}",
        employee_id=employee.employee_id,
        title="Trip",
        status="draft",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _quote(monkeypatch, rate: float, currency: str = "mxn") -> list[str]:
    """Stub the provider and record the dataset versions it was asked for."""
    asked: list[str] = []

    def fake_get(url, **_kwargs):
        version = url.split("currency-api@")[1].split("/")[0]
        asked.append(version)
        return httpx.Response(200, json={"date": "2026-08-21", currency: {"usd": rate}})

    monkeypatch.setattr(httpx, "get", fake_get)
    return asked


def _unavailable(monkeypatch) -> None:
    def fake_get(*_args, **_kwargs):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(httpx, "get", fake_get)


def test_a_foreign_line_is_restated_in_the_base_currency(db_session: Session, monkeypatch):
    _quote(monkeypatch, 0.059033125)
    owner = _employee(db_session, "fxowner")
    report = _report(db_session, owner, 31)

    item = create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN",
            amount_original=Decimal("204.76"),
            expense_date=date(2026, 8, 21),
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    # fx_rate stores six decimal places, so the quote is settled at that scale.
    assert item.fx_rate == Decimal("0.059033")
    assert item.amount_base == Decimal("12.09")


def test_the_rate_is_taken_for_the_day_the_money_was_spent(db_session: Session, monkeypatch):
    asked = _quote(monkeypatch, 0.059033125)
    owner = _employee(db_session, "fxdated")
    report = _report(db_session, owner, 32)

    create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("100"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    assert asked == ["2026-08-21"]


def test_a_base_currency_line_never_calls_the_provider(db_session: Session, monkeypatch):
    asked = _quote(monkeypatch, 0.059033125)
    owner = _employee(db_session, "fxusd")
    report = _report(db_session, owner, 33)

    item = create_item(
        report.report_id,
        ExpenseItemCreate(currency="USD", amount_original=Decimal("50.00")),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    assert asked == []
    assert item.fx_rate == Decimal(1)
    assert item.amount_base == Decimal("50.00")


def test_the_frozen_rate_is_re_resolved_when_the_line_is_edited(db_session: Session, monkeypatch):
    _quote(monkeypatch, 0.06)
    owner = _employee(db_session, "fxedit")
    report = _report(db_session, owner, 34)
    created = create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("100"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )
    assert created.amount_base == Decimal("6.00")

    fx.clear_cache()
    _quote(monkeypatch, 0.05)
    updated = update_item(
        created.item_id,
        ExpenseItemUpdate(amount_original=Decimal("200")),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    assert updated.fx_rate == Decimal("0.05")
    assert updated.amount_base == Decimal("10.00")


def test_an_unreachable_provider_never_invents_a_rate(db_session: Session, monkeypatch):
    _unavailable(monkeypatch)
    owner = _employee(db_session, "fxdown")
    report = _report(db_session, owner, 35)

    item = create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("204.76"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    # Face value, flagged — not a guessed conversion silently written to the total.
    assert item.fx_rate == Decimal(1)
    assert item.amount_base == Decimal("204.76")


def test_an_unconverted_line_is_flagged_for_the_approver(db_session: Session, monkeypatch):
    _unavailable(monkeypatch)
    owner = _employee(db_session, "fxflag")
    report = _report(db_session, owner, 36)
    create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("204.76"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    policies.replace_flags(db_session, db_session.get(ExpenseReports, report.report_id))

    codes = [
        flag.code
        for flag in db_session.exec(
            select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)
        ).all()
    ]
    assert "FX_RATE_UNAVAILABLE" in codes


def test_a_converted_line_raises_no_conversion_flag(db_session: Session, monkeypatch):
    _quote(monkeypatch, 0.059033125)
    owner = _employee(db_session, "fxclean")
    report = _report(db_session, owner, 37)
    create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("204.76"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    policies.replace_flags(db_session, db_session.get(ExpenseReports, report.report_id))

    codes = [
        flag.code
        for flag in db_session.exec(
            select(ExpenseReportFlags).where(ExpenseReportFlags.report_id == report.report_id)
        ).all()
    ]
    assert "FX_RATE_UNAVAILABLE" not in codes


def test_the_report_total_consolidates_mixed_currencies(db_session: Session, monkeypatch):
    _quote(monkeypatch, 0.06)
    owner = _employee(db_session, "fxmixed")
    report = _report(db_session, owner, 38)

    create_item(
        report.report_id,
        ExpenseItemCreate(
            currency="MXN", amount_original=Decimal("100"), expense_date=date(2026, 8, 21)
        ),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )
    create_item(
        report.report_id,
        ExpenseItemCreate(currency="USD", amount_original=Decimal("40")),
        db_session,
        owner,
        PLAIN_PERMISSIONS,
    )

    db_session.refresh(report)
    # 100 MXN @ 0.06 = 6.00, plus 40 USD.
    assert report.total_requested == Decimal("46.00")


def test_a_weekend_expense_falls_back_to_the_last_published_day(monkeypatch):
    asked: list[str] = []

    def fake_get(url, **_kwargs):
        version = url.split("currency-api@")[1].split("/")[0]
        asked.append(version)
        if version == "2026-08-16":  # Sunday: nothing published
            return httpx.Response(404)
        return httpx.Response(200, json={"date": version, "mxn": {"usd": 0.059}})

    monkeypatch.setattr(httpx, "get", fake_get)

    assert fx.rate_to_base("MXN", date(2026, 8, 16)) == Decimal("0.059")
    assert asked == ["2026-08-16", "2026-08-15"]


def test_a_resolved_rate_is_asked_for_once(monkeypatch):
    asked = _quote(monkeypatch, 0.059)

    fx.rate_to_base("MXN", date(2026, 8, 21))
    fx.rate_to_base("MXN", date(2026, 8, 21))

    assert len(asked) == 1
