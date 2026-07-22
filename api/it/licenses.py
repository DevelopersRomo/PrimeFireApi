"""Convenience routes for license catalog items (item_type = LICENSE)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, or_, select

from api.dependencies import require_module_permission
from api.it.catalog import _upsert_details, to_read_schema
from api.it.dependencies import get_current_employee_id, get_tenant_id
from bd.dependencies import get_db
from models.it.catalog import ITCatalogItems
from schemas.it.catalog import ItCatalogItemCreate, ItCatalogItemRead, ItCatalogItemUpdate

router = APIRouter()


@router.get("/", response_model=list[ItCatalogItemRead])
def list_licenses(
    search: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_licenses", "can_view")),
):
    statement = select(ITCatalogItems).where(
        ITCatalogItems.tenant_id == tenant_id,
        ITCatalogItems.item_type == "LICENSE",
    )
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                ITCatalogItems.name.ilike(pattern),  # type: ignore[attr-defined]
                ITCatalogItems.description.ilike(pattern),  # type: ignore[attr-defined]
            )
        )
    if not include_inactive:
        statement = statement.where(ITCatalogItems.is_active == True)  # noqa: E712
    items = db.exec(statement.order_by(ITCatalogItems.name)).all()
    return [to_read_schema(db, item) for item in items]


@router.get("/{catalog_item_id}", response_model=ItCatalogItemRead)
def get_license(
    catalog_item_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_licenses", "can_view")),
):
    item = db.get(ITCatalogItems, catalog_item_id)
    if not item or item.tenant_id != tenant_id or item.item_type != "LICENSE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License not found")
    return to_read_schema(db, item)


@router.post("/", response_model=ItCatalogItemRead, status_code=status.HTTP_201_CREATED)
def create_license(
    payload: ItCatalogItemCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_licenses", "can_create")),
):
    data = payload.model_dump(exclude={"service_details", "license_details"})
    data["item_type"] = "LICENSE"
    item = ITCatalogItems(tenant_id=tenant_id, created_by=employee_id, **data)
    db.add(item)
    db.flush()
    _upsert_details(db, item, None, payload.license_details)
    db.commit()
    db.refresh(item)
    return to_read_schema(db, item)


@router.patch("/{catalog_item_id}", response_model=ItCatalogItemRead)
def update_license(
    catalog_item_id: int,
    payload: ItCatalogItemUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_licenses", "can_edit")),
):
    item = db.get(ITCatalogItems, catalog_item_id)
    if not item or item.tenant_id != tenant_id or item.item_type != "LICENSE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License not found")

    data = payload.model_dump(exclude_unset=True, exclude={"service_details", "license_details", "item_type"})
    for key, value in data.items():
        setattr(item, key, value)

    db.add(item)
    _upsert_details(db, item, None, payload.license_details)
    db.commit()
    db.refresh(item)
    return to_read_schema(db, item)
