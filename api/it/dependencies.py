"""Shared dependencies for IT module routers."""

from fastapi import Depends
from sqlmodel import Session

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
from models.employees import Employees
from services.it.tenant_resolver import resolve_tenant_id


async def get_tenant_id(
    token_data: dict = Depends(require_authentication),
    db: Session = Depends(get_db),
) -> int:
    return resolve_tenant_id(token_data, db)


async def get_current_employee_id(
    employee: Employees = Depends(get_current_employee),
) -> int | None:
    return employee.employee_id
