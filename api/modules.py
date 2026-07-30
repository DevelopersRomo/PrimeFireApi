from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.modules import Modules
from schemas.modules import Module, ModuleCreate, ModuleListRead, ModuleUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


# ----------------------------
# 📌 CREATE MODULE
# ----------------------------
@router.post("", response_model=Module)
async def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("modules", "can_create")),
):
    """Create a new module."""
    # Check if module_key already exists
    existing = db.exec(select(Modules).where(Modules.module_key == module.module_key)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Module with key '{module.module_key}' already exists")

    # Validate parent_module_id if provided
    if module.parent_module_id:
        parent = db.exec(select(Modules).where(Modules.module_id == module.parent_module_id)).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent module with ID {module.parent_module_id} not found")

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ003
    db_module = Modules(**module.model_dump(), created_at=now_str, updated_at=now_str)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module


# ----------------------------
# 📌 READ ALL MODULES
# ----------------------------
@router.get("", response_model=list[Module] | PaginatedResponse[ModuleListRead])
async def get_modules(
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    _auth: dict = Depends(require_authentication),
):
    """Get all modules. By default, only active modules are returned."""
    query = select(Modules)
    if not include_inactive:
        query = query.where(Modules.is_active)
    query = query.order_by(Modules.display_order, Modules.module_name, Modules.module_id).offset(skip).limit(limit)
    modules = list(db.exec(query).all())
    if not with_meta:
        return modules

    parent_ids = {module.parent_module_id for module in modules if module.parent_module_id is not None}
    parent_names = {}
    if parent_ids:
        parent_names = dict(
            db.exec(select(Modules.module_id, Modules.module_name).where(Modules.module_id.in_(parent_ids))).all()
        )
    items = [
        ModuleListRead(
            **Module.model_validate(module).model_dump(),
            parent_module_name=parent_names.get(module.parent_module_id),
        )
        for module in modules
    ]
    count_query = select(func.count()).select_from(Modules)
    if not include_inactive:
        count_query = count_query.where(Modules.is_active)
    total = db.exec(count_query).one()
    return PaginatedResponse[ModuleListRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE MODULE
# ----------------------------
@router.get("/{module_id}", response_model=Module)
async def get_module(
    module_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_authentication)
):
    """Get a specific module by ID."""
    db_module = db.exec(select(Modules).where(Modules.module_id == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    return db_module


# ----------------------------
# 📌 GET MODULE BY KEY
# ----------------------------
@router.get("/by-key/{module_key}", response_model=Module)
async def get_module_by_key(
    module_key: str, db: Session = Depends(get_db), current_user: dict = Depends(require_authentication)
):
    """Get a specific module by its unique key."""
    db_module = db.exec(select(Modules).where(Modules.module_key == module_key)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail=f"Module with key '{module_key}' not found")
    return db_module


# ----------------------------
# 📌 GET CHILD MODULES
# ----------------------------
@router.get("/{module_id}/children", response_model=list[Module])
async def get_child_modules(
    module_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_authentication)
):
    """Get all child modules of a parent module."""
    query = (
        select(Modules)
        .where(Modules.parent_module_id == module_id, Modules.is_active)
        .order_by(Modules.display_order, Modules.module_name)
    )
    return db.exec(query).all()


# ----------------------------
# 📌 GET ROOT MODULES
# ----------------------------
@router.get("/root/all", response_model=list[Module])
async def get_root_modules(db: Session = Depends(get_db), current_user: dict = Depends(require_authentication)):
    """Get all root modules (modules without parent)."""
    query = (
        select(Modules)
        .where(Modules.parent_module_id is None, Modules.is_active)
        .order_by(Modules.display_order, Modules.module_name)
    )
    return db.exec(query).all()


# ----------------------------
# 📌 UPDATE MODULE
# ----------------------------
@router.put("/{module_id}", response_model=Module)
async def update_module(
    module_id: int,
    module: ModuleUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("modules", "can_edit")),
):
    """Update a module."""
    db_module = db.exec(select(Modules).where(Modules.module_id == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Check if module_key is being changed and if it already exists
    if module.module_key and module.module_key != db_module.module_key:
        existing = db.exec(select(Modules).where(Modules.module_key == module.module_key)).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Module with key '{module.module_key}' already exists")

    # Validate parent_module_id if being changed
    if module.parent_module_id is not None:
        if module.parent_module_id == module_id:
            raise HTTPException(status_code=400, detail="A module cannot be its own parent")
        parent = db.exec(select(Modules).where(Modules.module_id == module.parent_module_id)).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent module with ID {module.parent_module_id} not found")

    for key, value in module.model_dump(exclude_unset=True).items():
        setattr(db_module, key, value)

    db.commit()
    db.refresh(db_module)
    return db_module


# ----------------------------
# 📌 DELETE MODULE
# ----------------------------
@router.delete("/{module_id}")
async def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("modules", "can_delete")),
):
    """Delete a module. This will also delete all associated permissions."""
    db_module = db.exec(select(Modules).where(Modules.module_id == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Check if module has children
    children = db.exec(select(Modules).where(Modules.parent_module_id == module_id)).first()
    if children:
        raise HTTPException(
            status_code=400, detail="Cannot delete module with child modules. Delete or reassign children first."
        )

    db.delete(db_module)
    db.commit()
    return {"detail": "Module deleted successfully"}


# ----------------------------
# 📌 TOGGLE MODULE ACTIVE STATUS
# ----------------------------
@router.patch("/{module_id}/toggle-active", response_model=Module)
async def toggle_module_active(
    module_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("modules", "can_edit")),
):
    """Toggle the active status of a module."""
    db_module = db.exec(select(Modules).where(Modules.module_id == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")

    db_module.is_active = not db_module.is_active
    db.commit()
    db.refresh(db_module)
    return db_module
