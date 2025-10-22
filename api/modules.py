from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.modules import Modules
from schemas.modules import Module, ModuleCreate, ModuleUpdate

router = APIRouter()

# ----------------------------
# 📌 CREATE MODULE
# ----------------------------
@router.post("/", response_model=Module)
async def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Create a new module."""
    # Check if ModuleKey already exists
    existing = db.exec(select(Modules).where(Modules.ModuleKey == module.ModuleKey)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Module with key '{module.ModuleKey}' already exists")
    
    # Validate ParentModuleId if provided
    if module.ParentModuleId:
        parent = db.exec(select(Modules).where(Modules.ModuleId == module.ParentModuleId)).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent module with ID {module.ParentModuleId} not found")
    
    db_module = Modules(**module.model_dump())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

# ----------------------------
# 📌 READ ALL MODULES
# ----------------------------
@router.get("/", response_model=List[Module])
async def get_modules(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all modules. By default, only active modules are returned."""
    query = select(Modules)
    if not include_inactive:
        query = query.where(Modules.IsActive == True)
    query = query.order_by(Modules.DisplayOrder, Modules.ModuleName)
    return db.exec(query).all()

# ----------------------------
# 📌 READ ONE MODULE
# ----------------------------
@router.get("/{module_id}", response_model=Module)
async def get_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get a specific module by ID."""
    db_module = db.exec(select(Modules).where(Modules.ModuleId == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    return db_module

# ----------------------------
# 📌 GET MODULE BY KEY
# ----------------------------
@router.get("/by-key/{module_key}", response_model=Module)
async def get_module_by_key(
    module_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get a specific module by its unique key."""
    db_module = db.exec(select(Modules).where(Modules.ModuleKey == module_key)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail=f"Module with key '{module_key}' not found")
    return db_module

# ----------------------------
# 📌 GET CHILD MODULES
# ----------------------------
@router.get("/{module_id}/children", response_model=List[Module])
async def get_child_modules(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all child modules of a parent module."""
    query = select(Modules).where(
        Modules.ParentModuleId == module_id,
        Modules.IsActive == True
    ).order_by(Modules.DisplayOrder, Modules.ModuleName)
    return db.exec(query).all()

# ----------------------------
# 📌 GET ROOT MODULES
# ----------------------------
@router.get("/root/all", response_model=List[Module])
async def get_root_modules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Get all root modules (modules without parent)."""
    query = select(Modules).where(
        Modules.ParentModuleId == None,
        Modules.IsActive == True
    ).order_by(Modules.DisplayOrder, Modules.ModuleName)
    return db.exec(query).all()

# ----------------------------
# 📌 UPDATE MODULE
# ----------------------------
@router.put("/{module_id}", response_model=Module)
async def update_module(
    module_id: int,
    module: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authentication)
):
    """Update a module."""
    db_module = db.exec(select(Modules).where(Modules.ModuleId == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Check if ModuleKey is being changed and if it already exists
    if module.ModuleKey and module.ModuleKey != db_module.ModuleKey:
        existing = db.exec(select(Modules).where(Modules.ModuleKey == module.ModuleKey)).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Module with key '{module.ModuleKey}' already exists")
    
    # Validate ParentModuleId if being changed
    if module.ParentModuleId is not None:
        if module.ParentModuleId == module_id:
            raise HTTPException(status_code=400, detail="A module cannot be its own parent")
        parent = db.exec(select(Modules).where(Modules.ModuleId == module.ParentModuleId)).first()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent module with ID {module.ParentModuleId} not found")
    
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
    current_user: dict = Depends(require_authentication)
):
    """Delete a module. This will also delete all associated permissions."""
    db_module = db.exec(select(Modules).where(Modules.ModuleId == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Check if module has children
    children = db.exec(select(Modules).where(Modules.ParentModuleId == module_id)).first()
    if children:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete module with child modules. Delete or reassign children first."
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
    current_user: dict = Depends(require_authentication)
):
    """Toggle the active status of a module."""
    db_module = db.exec(select(Modules).where(Modules.ModuleId == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    db_module.IsActive = not db_module.IsActive
    db.commit()
    db.refresh(db_module)
    return db_module

