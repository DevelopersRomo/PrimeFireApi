from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import (
    ADMIN_ROLE_NAME,
    employee_has_admin_role,
    require_authentication,
    require_module_permission,
)
from api.inventory import INVENTORY_NOTIFICATION_ROLES
from bd.dependencies import get_db
from models.employees import Roles
from schemas.employees import Role, RoleCreate
from schemas.pagination import PaginatedResponse

router = APIRouter()

# Names that grant authority by themselves (impersonation, inventory approval).
RESERVED_ROLE_NAMES = {ADMIN_ROLE_NAME, *INVENTORY_NOTIFICATION_ROLES}


def _is_reserved(name: str | None) -> bool:
    return (name or "").strip().lower() in RESERVED_ROLE_NAMES


def _require_admin_for_reserved(db: Session, caller_permissions: dict, *names: str | None) -> None:
    """Only an Admin may create, rename into or out of, or delete an authority-bearing role."""
    if any(_is_reserved(name) for name in names) and not employee_has_admin_role(
        db, caller_permissions["employee"]["employee_id"]
    ):
        raise HTTPException(status_code=403, detail="Only an administrator can manage this role name.")


# ----------------------------
# 📌 CREATE ROLE
# ----------------------------
@router.post("", response_model=Role)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    caller_permissions: dict = Depends(require_module_permission("roles", "can_create")),
):
    """Create a new role."""
    _require_admin_for_reserved(db, caller_permissions, role.role_name)
    db_role = Roles(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


# ----------------------------
# 📌 READ ALL ROLES
# ----------------------------
@router.get("", response_model=list[Role] | PaginatedResponse[Role])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    _auth: dict = Depends(require_authentication),
):
    """Get all roles."""
    query = select(Roles).order_by(Roles.role_name, Roles.role_id).offset(skip).limit(limit)
    items = list(db.exec(query).all())
    if not with_meta:
        return items
    total = db.exec(select(func.count()).select_from(Roles)).one()
    return PaginatedResponse[Role](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE ROLE
# ----------------------------
@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_authentication)):
    """Get a specific role by ID."""
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


# ----------------------------
# 📌 UPDATE ROLE
# ----------------------------
@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role: RoleCreate,
    db: Session = Depends(get_db),
    caller_permissions: dict = Depends(require_module_permission("roles", "can_edit")),
):
    """Update a role."""
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    _require_admin_for_reserved(db, caller_permissions, db_role.role_name, role.role_name)

    for key, value in role.model_dump(exclude_unset=True).items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role


# ----------------------------
# 📌 DELETE ROLE
# ----------------------------
@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    caller_permissions: dict = Depends(require_module_permission("roles", "can_delete")),
):
    """Delete a role."""
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    _require_admin_for_reserved(db, caller_permissions, db_role.role_name)

    db.delete(db_role)
    db.commit()
    return {"detail": "Role deleted successfully"}
