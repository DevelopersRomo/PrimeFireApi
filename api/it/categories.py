from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from api.dependencies import require_module_permission
from api.it.dependencies import get_tenant_id
from bd.dependencies import get_db
from models.it.catalog import IT_ITEM_TYPES, ITCategories
from schemas.it.catalog import ItCategoryCreate, ItCategoryRead, ItCategoryUpdate

router = APIRouter()


def _validate_item_type(item_type: str | None) -> None:
    if item_type is not None and item_type not in IT_ITEM_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"item_type must be one of {IT_ITEM_TYPES}",
        )


@router.get("/", response_model=list[ItCategoryRead])
def list_categories(
    item_type: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_view")),
):
    statement = select(ITCategories).where(ITCategories.tenant_id == tenant_id)
    if item_type:
        statement = statement.where(ITCategories.item_type == item_type)
    if not include_inactive:
        statement = statement.where(ITCategories.is_active == True)  # noqa: E712
    return db.exec(statement.order_by(ITCategories.name)).all()


@router.get("/{category_id}", response_model=ItCategoryRead)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_view")),
):
    category = db.get(ITCategories, category_id)
    if not category or category.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=ItCategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: ItCategoryCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_create")),
):
    _validate_item_type(payload.item_type)
    category = ITCategories(tenant_id=tenant_id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=ItCategoryRead)
def update_category(
    category_id: int,
    payload: ItCategoryUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_edit")),
):
    category = db.get(ITCategories, category_id)
    if not category or category.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    data = payload.model_dump(exclude_unset=True)
    _validate_item_type(data.get("item_type"))
    for key, value in data.items():
        setattr(category, key, value)
    category.updated_at = datetime.utcnow()

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=ItCategoryRead)
def deactivate_category(
    category_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_delete")),
):
    """Soft delete: marks the category inactive."""
    category = db.get(ITCategories, category_id)
    if not category or category.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    category.is_active = False
    category.updated_at = datetime.utcnow()
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
