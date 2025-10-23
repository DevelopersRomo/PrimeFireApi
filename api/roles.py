from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.employees import Roles, Employees
from schemas.employees import Role, RoleCreate

router = APIRouter()

# ----------------------------
# 📌 CREATE ROLE
# ----------------------------
@router.post("/", response_model=Role)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
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
@router.get("/", response_model=List[Role])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all roles."""
    return db.exec(select(Roles)).all()

# ----------------------------
# 📌 READ ONE ROLE
# ----------------------------
@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get a specific role by ID."""
    db_role = db.exec(select(Roles).filter(Roles.RoleId == role_id)).first()
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
    current_user: dict = Depends(require_authentication)
):
    """Update a role."""
    db_role = db.exec(select(Roles).filter(Roles.RoleId == role_id)).first()
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
    current_user: dict = Depends(require_authentication)
):
    """Delete a role."""
    db_role = db.exec(select(Roles).filter(Roles.RoleId == role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(db_role)
    db.commit()
    return {"detail": "Role deleted successfully"}
