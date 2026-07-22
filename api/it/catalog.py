from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, or_, select

from api.dependencies import require_module_permission
from api.it.dependencies import get_current_employee_id, get_tenant_id
from bd.dependencies import get_db
from models.it.catalog import (
    IT_BILLING_CYCLES,
    IT_ITEM_TYPES,
    ITCatalogItems,
    ITLicenseDetails,
    ITServiceDetails,
)
from schemas.it.catalog import (
    ItCatalogItemCreate,
    ItCatalogItemRead,
    ItCatalogItemUpdate,
    ItLicenseDetailsPayload,
    ItServiceDetailsPayload,
)

router = APIRouter()


def to_read_schema(db: Session, item: ITCatalogItems) -> ItCatalogItemRead:
    service = db.get(ITServiceDetails, item.catalog_item_id)
    license_details = db.get(ITLicenseDetails, item.catalog_item_id)
    return ItCatalogItemRead(
        **item.model_dump(),
        service_details=ItServiceDetailsPayload(**service.model_dump(exclude={"catalog_item_id"})) if service else None,
        license_details=ItLicenseDetailsPayload(**license_details.model_dump(exclude={"catalog_item_id"}))
        if license_details
        else None,
    )


def _validate_enums(item_type: str | None, billing_cycle: str | None) -> None:
    if item_type is not None and item_type not in IT_ITEM_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"item_type must be one of {IT_ITEM_TYPES}",
        )
    if billing_cycle is not None and billing_cycle not in IT_BILLING_CYCLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"billing_cycle must be one of {IT_BILLING_CYCLES}",
        )


def _upsert_details(
    db: Session,
    item: ITCatalogItems,
    service_payload: ItServiceDetailsPayload | None,
    license_payload: ItLicenseDetailsPayload | None,
) -> None:
    if service_payload is not None:
        service = db.get(ITServiceDetails, item.catalog_item_id)
        if service:
            for key, value in service_payload.model_dump().items():
                setattr(service, key, value)
        else:
            service = ITServiceDetails(catalog_item_id=item.catalog_item_id, **service_payload.model_dump())
        db.add(service)

    if license_payload is not None:
        license_details = db.get(ITLicenseDetails, item.catalog_item_id)
        if license_details:
            for key, value in license_payload.model_dump().items():
                setattr(license_details, key, value)
        else:
            license_details = ITLicenseDetails(catalog_item_id=item.catalog_item_id, **license_payload.model_dump())
        db.add(license_details)


@router.get("/", response_model=list[ItCatalogItemRead])
def list_catalog_items(
    item_type: str | None = Query(default=None),
    billing_cycle: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_view")),
):
    statement = select(ITCatalogItems).where(ITCatalogItems.tenant_id == tenant_id)
    if item_type:
        statement = statement.where(ITCatalogItems.item_type == item_type)
    if billing_cycle:
        statement = statement.where(ITCatalogItems.billing_cycle == billing_cycle)
    if category_id:
        statement = statement.where(ITCatalogItems.category_id == category_id)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                ITCatalogItems.name.ilike(pattern),  # type: ignore[attr-defined]
                ITCatalogItems.description.ilike(pattern),  # type: ignore[attr-defined]
                ITCatalogItems.code.ilike(pattern),  # type: ignore[attr-defined]
            )
        )
    if not include_inactive:
        statement = statement.where(ITCatalogItems.is_active == True)  # noqa: E712

    items = db.exec(statement.order_by(ITCatalogItems.name)).all()
    return [to_read_schema(db, item) for item in items]


@router.get("/{catalog_item_id}", response_model=ItCatalogItemRead)
def get_catalog_item(
    catalog_item_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_view")),
):
    item = db.get(ITCatalogItems, catalog_item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")
    return to_read_schema(db, item)


@router.post("/", response_model=ItCatalogItemRead, status_code=status.HTTP_201_CREATED)
def create_catalog_item(
    payload: ItCatalogItemCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_catalog", "can_create")),
):
    _validate_enums(payload.item_type, payload.billing_cycle)
    data = payload.model_dump(exclude={"service_details", "license_details"})
    item = ITCatalogItems(tenant_id=tenant_id, created_by=employee_id, **data)
    db.add(item)
    db.flush()
    _upsert_details(db, item, payload.service_details, payload.license_details)
    db.commit()
    db.refresh(item)
    return to_read_schema(db, item)


@router.patch("/{catalog_item_id}", response_model=ItCatalogItemRead)
def update_catalog_item(
    catalog_item_id: int,
    payload: ItCatalogItemUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_edit")),
):
    item = db.get(ITCatalogItems, catalog_item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")

    data = payload.model_dump(exclude_unset=True, exclude={"service_details", "license_details"})
    _validate_enums(data.get("item_type"), data.get("billing_cycle"))
    for key, value in data.items():
        setattr(item, key, value)
    item.updated_at = datetime.utcnow()

    db.add(item)
    _upsert_details(db, item, payload.service_details, payload.license_details)
    db.commit()
    db.refresh(item)
    return to_read_schema(db, item)


@router.delete("/{catalog_item_id}", response_model=ItCatalogItemRead)
def deactivate_catalog_item(
    catalog_item_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_catalog", "can_delete")),
):
    """Soft delete: marks the catalog item inactive."""
    item = db.get(ITCatalogItems, catalog_item_id)
    if not item or item.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")

    item.is_active = False
    item.updated_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_read_schema(db, item)
