"""Admin impersonation: browse the app as another employee for a bounded time."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from api.dependencies import (
    employee_has_admin_role,
    employee_lookup_session,
    get_authenticated_employee,
    issue_impersonation_grant,
    simple_token_validator,
)
from bd.dependencies import get_db
from models.employees import Employees

router = APIRouter()


class ImpersonationStart(BaseModel):
    employee_id: int


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
    with employee_lookup_session(token_data, db) as (session, _owned):
        can_impersonate = employee_has_admin_role(session, real_employee.employee_id)

    return {
        "can_impersonate": can_impersonate,
        "real_employee_id": real_employee.employee_id,
    }


@router.post("/start", response_model=dict)
async def start_impersonation(
    payload: ImpersonationStart,
    real_employee: Employees = Depends(get_authenticated_employee),
    token_data: dict[str, Any] | None = Depends(simple_token_validator),
    db: Session = Depends(get_db),
):
    """Issue a signed, expiring grant for acting as `employee_id`.

    Authorisation is decided here from the real caller, and the grant carries
    its own expiry, so the client cannot extend the session by editing storage.
    """
    if payload.employee_id == real_employee.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already yourself.",
        )

    with employee_lookup_session(token_data, db) as (session, owned):
        if not employee_has_admin_role(session, real_employee.employee_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Impersonation requires the Admin role.",
            )

        target = session.exec(select(Employees).where(Employees.employee_id == payload.employee_id)).first()
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Impersonation target not found.",
            )
        display_name = target.display_name or target.email
        if owned:
            session.expunge(target)

    grant, expires_at = issue_impersonation_grant(real_employee.employee_id, payload.employee_id)

    return {
        "grant": grant,
        "expires_at": expires_at.isoformat(),
        "employee_id": payload.employee_id,
        "display_name": display_name,
    }
