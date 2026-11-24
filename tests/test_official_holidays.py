import re
from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, select

from models.countries import Countries
from models.employees import Employees
from models.time_off import Holiday
from services.official_holidays import COUNTRY_CODES, ensure_official_holidays, official_holidays

SEED_SQL = Path(__file__).resolve().parents[1] / "bd" / "sql" / "seed_official_holidays_2026_2027.sql"


def _seed_rows() -> set[tuple[str, str, str]]:
    """(code, date, name) rows of the seed script, checked by hand against each government's official list."""
    text = SEED_SQL.read_text(encoding="utf-8")
    return {
        (code, day, name.replace("''", "'"))
        for code, day, name in re.findall(r"\('(US|MX|DO|PR)', '(\d{4}-\d{2}-\d{2})', N'((?:[^']|'')*)'\)", text)
    }


@pytest.mark.parametrize("year", [2026, 2027])
def test_rules_match_the_official_lists(year: int):
    expected = {row for row in _seed_rows() if row[1].startswith(str(year))}
    generated = {(code, day.isoformat(), name) for code in COUNTRY_CODES for day, name in official_holidays(code, year)}
    assert generated == expected


def test_us_new_year_on_saturday_is_observed_the_previous_friday():
    days_2027 = dict(official_holidays("US", 2027))
    assert days_2027[date(2027, 12, 31)] == "New Year's Day 2028 (observed)"
    assert all(day.year == 2028 and (day.month, day.day) != (1, 1) for day, _ in official_holidays("US", 2028))


def test_do_restoration_day_is_not_moved_in_inauguration_years():
    names = {day.isoformat(): name for day, name in official_holidays("DO", 2028)}
    assert names["2028-08-16"] == "Restoration Day"


def test_ensure_creates_missing_countries_and_is_idempotent(db_session: Session):
    inserted = ensure_official_holidays(db_session, [2027])

    names = {c.name for c in db_session.exec(select(Countries)).all()}
    assert names == {"USA", "Mexico", "Dominican Republic", "Puerto Rico"}
    expected = sum(len(official_holidays(code, 2027)) for code in COUNTRY_CODES)
    assert inserted == len(db_session.exec(select(Holiday)).all()) == expected == 49
    assert ensure_official_holidays(db_session, [2027]) == 0


def test_ensure_targets_the_duplicate_row_employees_use_and_skips_global_dates(db_session: Session):
    mx_code = Countries(name="MX")
    mexico = Countries(name="México ")
    db_session.add_all([mx_code, mexico])
    db_session.commit()
    db_session.add(Employees(email="mx@example.com", first_name="A", last_name="B", country_id=mexico.country_id))
    db_session.add(Holiday(name="Company Day", date="2027-09-16", year=2027))
    db_session.commit()

    ensure_official_holidays(db_session, [2027])

    mx_days = {h.date for h in db_session.exec(select(Holiday).where(Holiday.country_id == mexico.country_id)).all()}
    assert "2027-12-25" in mx_days
    assert "2027-09-16" not in mx_days  # a global holiday already covers it
    assert not db_session.exec(select(Holiday).where(Holiday.country_id == mx_code.country_id)).all()
    assert db_session.exec(select(Countries).where(Countries.name == "Mexico")).first() is None
