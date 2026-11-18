from sqlmodel import or_, select

from models.employees import Employees
from models.time_off import Holiday


def holiday_country_filter(*country_ids: int | None):
    """WHERE clause for holidays that apply to the given countries: global ones plus each country's.

    No country (or only None) means global holidays only.
    """
    ids = {country_id for country_id in country_ids if country_id is not None}
    if not ids:
        return Holiday.country_id.is_(None)
    return or_(Holiday.country_id.is_(None), Holiday.country_id.in_(ids))


def employee_country_id(db, employee_id: int) -> int | None:
    return db.exec(select(Employees.country_id).where(Employees.employee_id == employee_id)).first()
