"""Official public holidays for USA, Mexico, Dominican Republic and Puerto Rico, computed per year.

Dates are the official day off (already moved/observed). Rules mirror the sources checked for 2026-2027
(see bd/sql/seed_official_holidays_2026_2027.sql); tests/test_official_holidays.py pins them to those lists.
"""

import logging
import unicodedata
from collections.abc import Iterable
from datetime import date, timedelta

from dateutil.easter import easter
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models.countries import Countries
from models.employees import Employees
from models.time_off import Holiday

logger = logging.getLogger(__name__)

COUNTRY_CODES = ("US", "MX", "DO", "PR")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)

# Name used when the country does not exist yet (same spelling as create_external_db.sql).
CANONICAL_NAMES = {"US": "USA", "MX": "Mexico", "DO": "Dominican Republic", "PR": "Puerto Rico"}
ALIASES = {
    "US": (
        "usa",
        "us",
        "u.s.",
        "u.s.a.",
        "united states",
        "united states of america",
        "america",
        "estados unidos",
        "eeuu",
        "ee.uu.",
    ),
    "MX": ("mexico", "mx", "mex", "estados unidos mexicanos"),
    "DO": ("dominican republic", "republica dominicana", "do", "rd", "dom"),
    "PR": ("puerto rico", "pr"),
}


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """n-th weekday of the month (n=-1 = last)."""
    if n > 0:
        first = date(year, month, 1)
        return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))
    last = date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def _us(year: int) -> list[tuple[date, str]]:
    """OPM federal holidays (5 U.S.C. 6103): Saturday is observed on Friday, Sunday on Monday."""
    days = [
        (_nth_weekday(year, 1, MON, 3), "Birthday of Martin Luther King, Jr."),
        (_nth_weekday(year, 2, MON, 3), "Washington's Birthday"),
        (_nth_weekday(year, 5, MON, -1), "Memorial Day"),
        (_nth_weekday(year, 9, MON, 1), "Labor Day"),
        (_nth_weekday(year, 10, MON, 2), "Columbus Day"),
        (_nth_weekday(year, 11, THU, 4), "Thanksgiving Day"),
    ]
    for month, day, name in (
        (1, 1, "New Year's Day"),
        (6, 19, "Juneteenth National Independence Day"),
        (7, 4, "Independence Day"),
        (11, 11, "Veterans Day"),
        (12, 25, "Christmas Day"),
    ):
        actual = date(year, month, day)
        if actual.weekday() == SAT:
            if (month, day) == (1, 1):
                continue  # observed on Dec 31 of the previous year
            days.append((actual - timedelta(days=1), f"{name} (observed)"))
        elif actual.weekday() == SUN:
            days.append((actual + timedelta(days=1), f"{name} (observed)"))
        else:
            days.append((actual, name))
    if date(year + 1, 1, 1).weekday() == SAT:
        days.append((date(year, 12, 31), f"New Year's Day {year + 1} (observed)"))
    return days


def _mx(year: int) -> list[tuple[date, str]]:
    """Ley Federal del Trabajo, art. 74.

    ponytail: the federal election day (art. 74 IX) is left out; add it by hand in election years.
    """
    days = [
        (date(year, 1, 1), "New Year's Day"),
        (_nth_weekday(year, 2, MON, 1), "Constitution Day"),
        (_nth_weekday(year, 3, MON, 3), "Benito Juarez's Birthday"),
        (date(year, 5, 1), "Labor Day"),
        (date(year, 9, 16), "Independence Day"),
        (_nth_weekday(year, 11, MON, 3), "Revolution Day"),
        (date(year, 12, 25), "Christmas Day"),
    ]
    if (year - 2024) % 6 == 0:
        days.append((date(year, 10, 1), "Transfer of Federal Executive Power"))
    return days


def _do_moved(actual: date, name: str) -> tuple[date, str]:
    """Ley 139-97: Tuesday/Wednesday move to the previous Monday, Thursday/Friday to the next one."""
    shift = {TUE: -1, WED: -2, THU: 4, FRI: 3}.get(actual.weekday())
    if shift is None:
        return actual, name
    return actual + timedelta(days=shift), f"{name} (moved from {MONTHS[actual.month - 1]} {actual.day})"


def _do(year: int) -> list[tuple[date, str]]:
    """Dominican Republic, as the Ministerio de Trabajo applies Ley 139-97 each year.

    ponytail: the Ministry publishes the official calendar every November (mt.gob.do); a decree that
    differs from the law has to be fixed by hand in the Holidays screen.
    """
    easter_day = easter(year)
    restoration = date(year, 8, 16)
    return [
        (date(year, 1, 1), "New Year's Day"),
        _do_moved(date(year, 1, 6), "Epiphany"),
        (date(year, 1, 21), "Our Lady of Altagracia"),
        _do_moved(date(year, 1, 26), "Duarte Day"),
        (date(year, 2, 27), "Independence Day"),
        (easter_day - timedelta(days=2), "Good Friday"),
        _do_moved(date(year, 5, 1), "Labor Day"),
        (easter_day + timedelta(days=60), "Corpus Christi"),
        # Not moved in presidential inauguration years (every 4 years: 2024, 2028...).
        (restoration, "Restoration Day") if year % 4 == 0 else _do_moved(restoration, "Restoration Day"),
        (date(year, 9, 24), "Our Lady of Mercedes"),
        _do_moved(date(year, 11, 6), "Constitution Day"),
        (date(year, 12, 25), "Christmas Day"),
    ]


def _pr(year: int) -> list[tuple[date, str]]:
    """Puerto Rico government holidays as listed by OATRH (actual dates, not moved)."""
    days = [
        (date(year, 1, 1), "New Year's Day"),
        (date(year, 1, 6), "Three Kings Day"),
        (_nth_weekday(year, 1, MON, 3), "Birthday of Martin Luther King, Jr."),
        (_nth_weekday(year, 2, MON, 3), "Presidents' Day and Puerto Rican Patriots Day"),
        (date(year, 3, 2), "American Citizenship Day"),
        (date(year, 3, 22), "Emancipation Day"),
        (easter(year) - timedelta(days=2), "Good Friday"),
        (_nth_weekday(year, 5, MON, -1), "Memorial Day"),
        (date(year, 6, 19), "Juneteenth National Independence Day"),
        (date(year, 7, 4), "Independence Day"),
        (date(year, 7, 25), "Puerto Rico Constitution Day"),
        (date(year, 7, 27), "Jose Celso Barbosa Day"),
        (_nth_weekday(year, 9, MON, 1), "Labor Day"),
        (_nth_weekday(year, 10, MON, 2), "Columbus Day"),
        (date(year, 11, 11), "Veterans Day"),
        (date(year, 11, 19), "Puerto Rican Heritage Day"),
        (_nth_weekday(year, 11, THU, 4), "Thanksgiving Day"),
        (date(year, 12, 25), "Christmas Day"),
    ]
    if year % 4 == 0:  # general elections: first Tuesday after the first Monday of November
        days.append((_nth_weekday(year, 11, MON, 1) + timedelta(days=1), "General Election Day"))
    return days


_RULES = {"US": _us, "MX": _mx, "DO": _do, "PR": _pr}


def official_holidays(code: str, year: int) -> list[tuple[date, str]]:
    return sorted(_RULES[code](year))


def _normalize(name: str | None) -> str:
    text = unicodedata.normalize("NFKD", (name or "").strip().casefold())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _target_country_ids(db: Session) -> dict[str, list[int]]:
    """Country rows per code. Duplicates ("MX" and "Mexico"): every row employees use, else the lowest id.
    A country with no matching row is created.
    """
    employees = dict(
        db.exec(
            select(Employees.country_id, func.count())
            .where(Employees.country_id.is_not(None))
            .group_by(Employees.country_id)
        ).all()
    )
    matches: dict[str, list[int]] = {code: [] for code in COUNTRY_CODES}
    for country in db.exec(select(Countries).order_by(Countries.country_id)).all():
        for code, aliases in ALIASES.items():
            if _normalize(country.name) in aliases:
                matches[code].append(country.country_id)

    targets = {}
    for code, matched_ids in matches.items():
        ids = matched_ids
        if not ids:
            country = Countries(name=CANONICAL_NAMES[code])
            db.add(country)
            db.commit()
            db.refresh(country)
            ids = [country.country_id]
        used = [country_id for country_id in ids if employees.get(country_id)]
        targets[code] = used or ids[:1]
    return targets


def ensure_official_holidays(db: Session, years: Iterable[int]) -> int:
    """Insert the official holidays of `years` that are missing. Never updates or deletes.

    A date is skipped when that country, or a global holiday (country_id NULL), already has one.
    Returns how many holidays were inserted.
    """
    years = list(years)
    targets = _target_country_ids(db)
    taken = {
        (h_date, country_id)
        for h_date, country_id in db.exec(select(Holiday.date, Holiday.country_id).where(Holiday.year.in_(years))).all()
    }

    inserted = 0
    for code, country_ids in targets.items():
        for year in years:
            for day, name in official_holidays(code, year):
                key = day.isoformat()
                for country_id in country_ids:
                    if (key, country_id) in taken or (key, None) in taken:
                        continue
                    db.add(Holiday(name=name, date=key, year=year, country_id=country_id))
                    try:
                        db.commit()
                    except IntegrityError:
                        # A legacy UNIQUE(date) (bd/sql/time_off.sql) rejects the same date in two countries.
                        db.rollback()
                        logger.warning(
                            f"[HOLIDAYS] Could not insert {key} for country {country_id}: date already taken"
                        )
                        continue
                    taken.add((key, country_id))
                    inserted += 1
    return inserted
