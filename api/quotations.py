from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_
from sqlmodel import Session, select

from api.dependencies import require_authentication, require_module_permission
from bd.dependencies import get_db
from models.quotations import Quotations
from schemas.pagination import PaginatedResponse
from schemas.quotations import (
    QuotationCreate,
    QuotationRead,
    QuotationUpdate,
)

router = APIRouter(
    prefix="/quotations",
    tags=["quotations"],
)


# ----------------------------
# CREATE
# POST /quotations/
# ----------------------------
@router.post(
    "/",
    response_model=QuotationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation(
    quotation: QuotationCreate,
    db: Session = Depends(get_db),
    _perms: dict = Depends(require_module_permission("quotations", "can_create")),
):
    db_quotation = Quotations(**quotation.model_dump(by_alias=False))

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# READ ALL
# GET /quotations/
# ----------------------------
@router.get("/", response_model=list[QuotationRead] | PaginatedResponse[QuotationRead])
def get_quotations(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    search: str | None = Query(None),
    quote_from: date | None = Query(None),
    quote_to: date | None = Query(None),
    created_from: date | None = Query(None),
    created_to: date | None = Query(None),
    sort_field: str = Query(
        "created_at",
        pattern="^(id|customer_id|quote_date|expiration_date|subtotal|tax|discount|total|status|created_at)$",
    ),
    sort_direction: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    filters = []
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        searchable_columns = [
            Quotations.id,
            Quotations.customer_id,
            Quotations.quote_date,
            Quotations.expiration_date,
            Quotations.subtotal,
            Quotations.tax,
            Quotations.discount,
            Quotations.total,
            Quotations.status,
            Quotations.notes,
            Quotations.created_at,
        ]
        filters.append(or_(*[func.lower(cast(column, String)).like(term) for column in searchable_columns]))
    if quote_from:
        filters.append(Quotations.quote_date >= quote_from)
    if quote_to:
        filters.append(Quotations.quote_date < quote_to + timedelta(days=1))
    if created_from:
        filters.append(Quotations.created_at >= created_from)
    if created_to:
        filters.append(Quotations.created_at < created_to + timedelta(days=1))

    sort_columns = {
        "id": Quotations.id,
        "customer_id": Quotations.customer_id,
        "quote_date": Quotations.quote_date,
        "expiration_date": Quotations.expiration_date,
        "subtotal": Quotations.subtotal,
        "tax": Quotations.tax,
        "discount": Quotations.discount,
        "total": Quotations.total,
        "status": Quotations.status,
        "created_at": Quotations.created_at,
    }
    sort_column = sort_columns[sort_field]
    order = sort_column.asc() if sort_direction == "asc" else sort_column.desc()
    tie_breaker = Quotations.id.asc() if sort_direction == "asc" else Quotations.id.desc()

    statement = select(Quotations).where(*filters).order_by(order)
    if sort_field != "id":
        statement = statement.order_by(tie_breaker)
    statement = statement.offset(skip).limit(limit)
    items = db.exec(statement).all()

    if not with_meta:
        return items

    total = db.exec(select(func.count()).select_from(Quotations).where(*filters)).one()
    return PaginatedResponse[QuotationRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# READ ONE
# GET /quotations/{quotation_id}
# ----------------------------
@router.get("/{quotation_id}", response_model=QuotationRead)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    quotation = db.get(Quotations, quotation_id)

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    return quotation


# ----------------------------
# UPDATE (PUT)
# PUT /quotations/{quotation_id}
# ----------------------------
@router.put("/{quotation_id}", response_model=QuotationRead)
def update_quotation(
    quotation_id: int,
    quotation: QuotationCreate,
    db: Session = Depends(get_db),
    _perms: dict = Depends(require_module_permission("quotations", "can_edit")),
):
    db_quotation = db.get(Quotations, quotation_id)

    if not db_quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    data = quotation.model_dump(by_alias=False)

    for key, value in data.items():
        setattr(db_quotation, key, value)

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# PATCH
# PATCH /quotations/{quotation_id}
# ----------------------------
@router.patch("/{quotation_id}", response_model=QuotationRead)
def patch_quotation(
    quotation_id: int,
    quotation: QuotationUpdate,
    db: Session = Depends(get_db),
    _perms: dict = Depends(require_module_permission("quotations", "can_edit")),
):
    db_quotation = db.get(Quotations, quotation_id)

    if not db_quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    update_data = quotation.model_dump(exclude_unset=True, by_alias=False)

    for key, value in update_data.items():
        setattr(db_quotation, key, value)

    db.add(db_quotation)
    db.commit()
    db.refresh(db_quotation)

    return db_quotation


# ----------------------------
# DELETE
# DELETE /quotations/{quotation_id}
# ----------------------------
@router.delete("/{quotation_id}", status_code=status.HTTP_200_OK)
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    _perms: dict = Depends(require_module_permission("quotations", "can_delete")),
):
    quotation = db.get(Quotations, quotation_id)

    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    db.delete(quotation)
    db.commit()

    return {"message": "Quotation deleted successfully"}
