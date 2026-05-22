from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.hardware_inventory import HardwareInventory
from schemas.hardware_inventory import HardwareInventoryCreate, HardwareInventoryRead, HardwareInventoryUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=HardwareInventoryRead)
def create_hardware(
    hardware: HardwareInventoryCreate, db: Session = Depends(get_db), _auth=Depends(require_authentication)
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
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = (
        select(HardwareInventory)
        .options(selectinload(HardwareInventory.employee))
        .order_by(HardwareInventory.created_at.desc(), HardwareInventory.hardware_id.desc())
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()

    if not with_meta:
        return items

    total = db.exec(select(func.count()).select_from(HardwareInventory)).one()
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
    _auth=Depends(require_authentication),
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
def delete_hardware(hardware_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_hardware = db.exec(select(HardwareInventory).filter(HardwareInventory.hardware_id == hardware_id)).first()
    if not db_hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    db.delete(db_hardware)
    db.commit()
    return {"message": "Hardware deleted successfully"}
