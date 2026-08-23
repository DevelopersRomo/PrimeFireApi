"""Local-only employee impersonation support for the frontend."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.dependencies import (
    employee_has_admin_role,
    employee_lookup_session,
    get_authenticated_employee,
    impersonation_enabled,
    simple_token_validator,
)
from bd.dependencies import get_db
from models.employees import Employees

router = APIRouter()


@router.get("/context", response_model=dict)
async def get_impersonation_context(
    real_employee: Employees = Depends(get_authenticated_employee),
    token_data: dict[str, Any] | None = Depends(simple_token_validator),
    db: Session = Depends(get_db),
):
    """Tell the frontend whether the real caller may impersonate other employees.

    Resolved from the real caller, never from an impersonated one, so the
    switch stays reachable while impersonation is active.
    """
    if not impersonation_enabled():
        return {"can_impersonate": False}

    with employee_lookup_session(token_data, db) as (session, _owned):
        can_impersonate = employee_has_admin_role(session, real_employee.employee_id)

    return {
        "can_impersonate": can_impersonate,
        "real_employee_id": real_employee.employee_id,
    }
