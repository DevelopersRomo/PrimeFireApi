from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.employees import Employees
from models.licenses import Licenses
from schemas.licenses import License, LicenseCreate, LicenseRead, LicenseUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=License)
def create_license(
    license: LicenseCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("licenses", "can_create")),
):
    db_license = Licenses(**license.model_dump())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[LicenseRead] | PaginatedResponse[LicenseRead])
def get_licenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    search: str | None = Query(None),
    created_from: date | None = Query(None),
    created_to: date | None = Query(None),
    expiry_from: date | None = Query(None),
    expiry_to: date | None = Query(None),
    sort_by: str = Query(
        "created_at", pattern="^(software|version|created_at|expiry_date|key|account|password|employee)$"
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
                Licenses.software.ilike(term),
                Licenses.version.ilike(term),
                Licenses.key.ilike(term),
                Licenses.account.ilike(term),
                Licenses.password.ilike(term),
                Employees.display_name.ilike(term),
            )
        )
    if created_from:
        filters.append(Licenses.created_at >= datetime.combine(created_from, datetime.min.time()))
    if created_to:
        filters.append(Licenses.created_at <= datetime.combine(created_to, datetime.max.time()))
    if expiry_from:
        filters.append(Licenses.expiry_date >= expiry_from)
    if expiry_to:
        filters.append(Licenses.expiry_date <= expiry_to)

    sort_columns = {
        "software": Licenses.software,
        "version": Licenses.version,
        "created_at": Licenses.created_at,
        "expiry_date": Licenses.expiry_date,
        "key": Licenses.key,
        "account": Licenses.account,
        "password": Licenses.password,
        "employee": Employees.display_name,
    }
    sort_column = sort_columns[sort_by]
    ordering = sort_column.asc() if sort_dir == "asc" else sort_column.desc()

    statement = select(Licenses).join(Employees, Licenses.employee_id == Employees.employee_id, isouter=True)
    if filters:
        statement = statement.where(*filters)
    statement = (
        statement.options(selectinload(Licenses.employee))
        .order_by(ordering, Licenses.license_id.asc() if sort_dir == "asc" else Licenses.license_id.desc())
        .offset(skip)
        .limit(limit)
    )
    items = db.exec(statement).all()

    if not with_meta:
        return items

    count_query = (
        select(func.count())
        .select_from(Licenses)
        .join(Employees, Licenses.employee_id == Employees.employee_id, isouter=True)
    )
    if filters:
        count_query = count_query.where(*filters)
    total = db.exec(count_query).one()
    return PaginatedResponse[LicenseRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{license_id}", response_model=License)
def get_license(license_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return db_license


# ----------------------------
# 📌 UPDATE (PUT - full update)
# ----------------------------
@router.put("/{license_id}", response_model=License)
def update_license(
    license_id: int,
    license: LicenseCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("licenses", "can_edit")),
):
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    for key, value in license.model_dump().items():
        setattr(db_license, key, value)

    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 UPDATE (PATCH - partial update)
# ----------------------------
@router.patch("/{license_id}", response_model=License)
def patch_license(
    license_id: int,
    license: LicenseUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("licenses", "can_edit")),
):
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    update_data = license.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_license, key, value)

    db.commit()
    db.refresh(db_license)
    return db_license


# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{license_id}")
def delete_license(
    license_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("licenses", "can_delete")),
):
    db_license = db.exec(select(Licenses).filter(Licenses.license_id == license_id)).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    db.delete(db_license)
    db.commit()
    return {"message": "License deleted successfully"}
