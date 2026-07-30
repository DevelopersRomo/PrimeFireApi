from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Date, String, cast, func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.employees import Employees
from models.hardware_inventory import HardwareInventory
from schemas.hardware_inventory import HardwareInventoryCreate, HardwareInventoryRead, HardwareInventoryUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=HardwareInventoryRead)
def create_hardware(
    hardware: HardwareInventoryCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("hardware", "can_create")),
):
    db_hardware = HardwareInventory(**hardware.model_dump())
    db.add(db_hardware)
    db.commit()
    db.refresh(db_hardware)
    return db_hardware


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[HardwareInventoryRead] | PaginatedResponse[HardwareInventoryRead])
def get_hardware_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    warranty_from: date | None = Query(None),
    warranty_to: date | None = Query(None),
    created_from: date | None = Query(None),
    created_to: date | None = Query(None),
    sort_by: str = Query(
        "created_at",
        pattern="^(hardware_id|serial_number|brand|model|device_type|processor|ram_gb|storage_type|storage_size_gb|gpu|operating_system|warranty_start_date|warranty_end_date|employee|location|status|created_at|updated_at)$",
    ),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    filters = []
    if search and search.strip():
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                cast(HardwareInventory.hardware_id, String).ilike(term),
                HardwareInventory.serial_number.ilike(term),
                HardwareInventory.brand.ilike(term),
                HardwareInventory.model.ilike(term),
                HardwareInventory.device_type.ilike(term),
                HardwareInventory.processor.ilike(term),
                cast(HardwareInventory.ram_gb, String).ilike(term),
                HardwareInventory.storage_type.ilike(term),
                cast(HardwareInventory.storage_size_gb, String).ilike(term),
                HardwareInventory.gpu.ilike(term),
                HardwareInventory.operating_system.ilike(term),
                Employees.display_name.ilike(term),
                HardwareInventory.location.ilike(term),
                HardwareInventory.status.ilike(term),
                HardwareInventory.notes.ilike(term),
            )
        )
    if status_filter:
        filters.append(func.lower(HardwareInventory.status) == status_filter.lower())
    if warranty_from:
        filters.append(HardwareInventory.warranty_end_date >= warranty_from)
    if warranty_to:
        filters.append(HardwareInventory.warranty_end_date <= warranty_to)
    if created_from:
        filters.append(cast(HardwareInventory.created_at, Date) >= created_from)
    if created_to:
        filters.append(cast(HardwareInventory.created_at, Date) <= created_to)

    sort_columns = {
        "hardware_id": HardwareInventory.hardware_id,
        "serial_number": HardwareInventory.serial_number,
        "brand": HardwareInventory.brand,
        "model": HardwareInventory.model,
        "device_type": HardwareInventory.device_type,
        "processor": HardwareInventory.processor,
        "ram_gb": HardwareInventory.ram_gb,
        "storage_type": HardwareInventory.storage_type,
        "storage_size_gb": HardwareInventory.storage_size_gb,
        "gpu": HardwareInventory.gpu,
        "operating_system": HardwareInventory.operating_system,
        "warranty_start_date": HardwareInventory.warranty_start_date,
        "warranty_end_date": HardwareInventory.warranty_end_date,
        "employee": Employees.display_name,
        "location": HardwareInventory.location,
        "status": HardwareInventory.status,
        "created_at": HardwareInventory.created_at,
        "updated_at": HardwareInventory.updated_at,
    }
    sort_column = sort_columns[sort_by]
    ordering = sort_column.asc() if sort_dir == "asc" else sort_column.desc()

    statement = select(HardwareInventory).join(
        Employees, HardwareInventory.employee_id == Employees.employee_id, isouter=True
    )
    if filters:
        statement = statement.where(*filters)
    statement = (
        statement.options(selectinload(HardwareInventory.employee))
        .order_by(
            ordering,
            HardwareInventory.hardware_id.asc() if sort_dir == "asc" else HardwareInventory.hardware_id.desc(),
        )
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()

    if not with_meta:
        return items

    count_query = (
        select(func.count())
        .select_from(HardwareInventory)
        .join(Employees, HardwareInventory.employee_id == Employees.employee_id, isouter=True)
    )
    if filters:
        count_query = count_query.where(*filters)
    total = db.exec(count_query).one()
    return PaginatedResponse[HardwareInventoryRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{hardware_id}", response_model=HardwareInventoryRead)
def get_hardware(hardware_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_hardware = db.exec(select(HardwareInventory).filter(HardwareInventory.hardware_id == hardware_id)).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    return db_hardware


# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{hardware_id}", response_model=HardwareInventoryRead)
def update_hardware(
    hardware_id: int,
    hardware: HardwareInventoryUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("hardware", "can_edit")),
):
    db_hardware = db.exec(select(HardwareInventory).filter(HardwareInventory.hardware_id == hardware_id)).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    for key, value in hardware.model_dump(exclude_unset=True).items():
        setattr(db_hardware, key, value)

    db_hardware.updated_at = hardware.updated_at or None
    db.commit()
    db.refresh(db_hardware)
    return db_hardware


# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{hardware_id}")
def delete_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("hardware", "can_delete")),
):
    db_hardware = db.exec(select(HardwareInventory).filter(HardwareInventory.hardware_id == hardware_id)).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    db.delete(db_hardware)
    db.commit()
    return {"message": "Hardware deleted successfully"}
