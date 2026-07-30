from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.employees import Roles
from schemas.employees import Role, RoleCreate
from schemas.pagination import PaginatedResponse

router = APIRouter()


# ----------------------------
# 📌 CREATE ROLE
# ----------------------------
@router.post("", response_model=Role)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("roles", "can_create")),
):
    """Create a new role."""
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
    _permissions: dict = Depends(require_module_permission("roles", "can_edit")),
):
    """Update a role."""
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

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
    _permissions: dict = Depends(require_module_permission("roles", "can_delete")),
):
    """Delete a role."""
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(db_role)
    db.commit()
    return {"detail": "Role deleted successfully"}
