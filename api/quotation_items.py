from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.quotation_items import QuotationItems
from models.quotations import Quotations
from schemas.quotation_items import (
    QuotationItemCreate,
    QuotationItemRead,
    QuotationItemUpdate,
)

router = APIRouter(prefix="/quotations/{quotation_id}/items", tags=["quotation_items"])


def ensure_quotation_exists(db: Session, quotation_id: int) -> None:
    quotation = db.get(Quotations, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")


def get_quotation_item_or_404(db: Session, quotation_id: int, item_id: int) -> QuotationItems:
    statement = select(QuotationItems).where(
        QuotationItems.id == item_id,
        QuotationItems.quotation_id == quotation_id,
    )
    item = db.exec(statement).first()

    if not item:
        raise HTTPException(status_code=404, detail="Quotation item not found")

    return item


@router.post(
    "/",
    response_model=QuotationItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation_item(
    quotation_id: int,
    payload: QuotationItemCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)

    db_item = QuotationItems(quotation_id=quotation_id, **payload.model_dump(by_alias=False))

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[QuotationItemRead])
def get_quotation_items(
    quotation_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)

    statement = select(QuotationItems).where(QuotationItems.quotation_id == quotation_id)
    return db.exec(statement).all()


@router.get("/{item_id}", response_model=QuotationItemRead)
def get_quotation_item(
    quotation_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)
    return get_quotation_item_or_404(db, quotation_id, item_id)


@router.put("/{item_id}", response_model=QuotationItemRead)
def update_quotation_item(
    quotation_id: int,
    item_id: int,
    payload: QuotationItemCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)
    db_item = get_quotation_item_or_404(db, quotation_id, item_id)

    data = payload.model_dump(by_alias=False)
    for key, value in data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.patch("/{item_id}", response_model=QuotationItemRead)
def patch_quotation_item(
    quotation_id: int,
    item_id: int,
    payload: QuotationItemUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)
    db_item = get_quotation_item_or_404(db, quotation_id, item_id)

    update_data = payload.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_quotation_item(
    quotation_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    ensure_quotation_exists(db, quotation_id)
    db_item = get_quotation_item_or_404(db, quotation_id, item_id)

    db.delete(db_item)
    db.commit()

    return {"message": "Quotation item deleted successfully"}
