from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func
from sqlalchemy import select as sa_select
from sqlmodel import Session, or_, select

from api.dependencies import require_module_permission
from api.it.dependencies import get_current_employee_id, get_tenant_id
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from models.it.documents import ITQuotationDocuments
from models.it.quotations import (
    ITPaymentSchedule,
    ITQuotationItems,
    ITQuotationNotes,
    ITQuotationStatusHistory,
    ITQuotationTerms,
    ITQuotations,
)
from schemas.it.documents import ItQuotationDocumentRead
from schemas.it.quotations import (
    ItPaymentScheduleEntry,
    ItPaymentScheduleRead,
    ItQuotationCreate,
    ItQuotationDetail,
    ItQuotationItemCreate,
    ItQuotationItemRead,
    ItQuotationItemUpdate,
    ItQuotationItemsReorder,
    ItQuotationNoteCreate,
    ItQuotationNoteRead,
    ItQuotationRead,
    ItQuotationReportMetrics,
    ItQuotationReportResponse,
    ItQuotationStatusChange,
    ItQuotationTermsPayload,
    ItQuotationUpdate,
    ItStatusHistoryRead,
)
from schemas.pagination import PaginatedResponse
from services.it import quote_service
from services.it.email_service import send_quotation_email
from services.it.pdf_service import generate_quotation_pdf
from services.it.quote_calculator import calculate_line

router = APIRouter()

SENT_REPORT_STATUSES = ("SENT", "VIEWED", "ACCEPTED", "REJECTED")


def _get_quotation(db: Session, tenant_id: int, quotation_id: int) -> ITQuotations:
    quotation = db.get(ITQuotations, quotation_id)
    if not quotation or quotation.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
    return quotation


def _to_detail(db: Session, quotation: ITQuotations) -> ItQuotationDetail:
    items = db.exec(
        select(ITQuotationItems)
        .where(ITQuotationItems.quotation_id == quotation.quotation_id)
        .order_by(ITQuotationItems.sort_order, ITQuotationItems.quotation_item_id)
    ).all()
    terms = db.get(ITQuotationTerms, quotation.quotation_id)
    schedule = db.exec(
        select(ITPaymentSchedule)
        .where(ITPaymentSchedule.quotation_id == quotation.quotation_id)
        .order_by(ITPaymentSchedule.sequence_number)
    ).all()
    return ItQuotationDetail(
        **quotation.model_dump(),
        items=[ItQuotationItemRead(**i.model_dump()) for i in items],
        terms=ItQuotationTermsPayload(**terms.model_dump(exclude={"quotation_id"})) if terms else None,
        payment_schedule=[ItPaymentScheduleRead(**s.model_dump()) for s in schedule],
    )


# ----------------------------
# Quotation CRUD
# ----------------------------
def _quotation_filters(
    tenant_id: int,
    status_filter: str | None = None,
    customer_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    statuses: tuple[str, ...] | None = None,
) -> list:
    filters = [ITQuotations.tenant_id == tenant_id]
    if status_filter:
        filters.append(ITQuotations.status == status_filter)
    if statuses:
        filters.append(ITQuotations.status.in_(statuses))  # type: ignore[attr-defined]
    if customer_id is not None:
        filters.append(ITQuotations.customer_id == customer_id)
    if date_from:
        filters.append(ITQuotations.quote_date >= date_from)
    if date_to:
        filters.append(ITQuotations.quote_date <= date_to)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                ITQuotations.quotation_number.ilike(pattern),  # type: ignore[attr-defined]
                ITQuotations.customer_name_snapshot.ilike(pattern),  # type: ignore[attr-defined]
            )
        )
    return filters


@router.get("/", response_model=list[ItQuotationRead] | PaginatedResponse[ItQuotationRead])
def list_quotations(
    status_filter: str | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    search: str | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    filters = _quotation_filters(
        tenant_id,
        status_filter,
        customer_id,
        date_from,
        date_to,
        search,
    )
    statement = (
        select(ITQuotations)
        .where(*filters)
        .order_by(ITQuotations.created_at.desc(), ITQuotations.quotation_id.desc())  # type: ignore[attr-defined]
        .offset(skip)
        .limit(limit)
    )
    quotation_rows = db.exec(statement).all()
    if not with_meta:
        return quotation_rows

    items = [ItQuotationRead.model_validate(row, from_attributes=True) for row in quotation_rows]
    total = db.exec(select(func.count()).select_from(ITQuotations).where(*filters)).one()
    return PaginatedResponse[ItQuotationRead](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


@router.get("/report", response_model=ItQuotationReportResponse)
def get_sent_quotation_report(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_dashboard", "can_view")),
):
    filters = _quotation_filters(
        tenant_id,
        date_from=date_from,
        date_to=date_to,
        statuses=SENT_REPORT_STATUSES,
    )
    quotation_rows = db.exec(
        select(ITQuotations)
        .where(*filters)
        .order_by(ITQuotations.quote_date.desc(), ITQuotations.quotation_id.desc())  # type: ignore[attr-defined]
        .offset(skip)
        .limit(limit)
    ).all()
    items = [ItQuotationRead.model_validate(row, from_attributes=True) for row in quotation_rows]
    aggregate = db.execute(
        sa_select(
            func.count(),
            func.coalesce(func.sum(ITQuotations.initial_total), 0),
            func.coalesce(func.sum(ITQuotations.monthly_recurring_subtotal), 0),
            func.coalesce(func.sum(ITQuotations.annual_recurring_subtotal), 0),
            func.sum(case((ITQuotations.status == "SENT", 1), else_=0)),
            func.sum(case((ITQuotations.status == "VIEWED", 1), else_=0)),
            func.sum(case((ITQuotations.status == "ACCEPTED", 1), else_=0)),
            func.sum(case((ITQuotations.status == "REJECTED", 1), else_=0)),
        )
        .select_from(ITQuotations)
        .where(*filters)
    ).one()
    total = aggregate[0]
    accepted = aggregate[6] or 0
    metrics = ItQuotationReportMetrics(
        sent_count=total,
        total_amount=aggregate[1] or Decimal(0),
        monthly_recurring=aggregate[2] or Decimal(0),
        annual_recurring=aggregate[3] or Decimal(0),
        conversion_rate=Decimal(accepted * 100) / Decimal(total) if total else Decimal(0),
        sent_status_count=aggregate[4] or 0,
        viewed_status_count=aggregate[5] or 0,
        accepted_status_count=accepted,
        rejected_status_count=aggregate[7] or 0,
    )
    return ItQuotationReportResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
        metrics=metrics,
    )


@router.get("/{quotation_id}", response_model=ItQuotationDetail)
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    return _to_detail(db, _get_quotation(db, tenant_id, quotation_id))


@router.post("/", response_model=ItQuotationDetail, status_code=status.HTTP_201_CREATED)
def create_quotation(
    payload: ItQuotationCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_create")),
):
    quotation = quote_service.create_quotation(db, payload, tenant_id, created_by=employee_id)
    return _to_detail(db, quotation)


@router.patch("/{quotation_id}", response_model=ItQuotationDetail)
def update_quotation(
    quotation_id: int,
    payload: ItQuotationUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    data = payload.model_dump(exclude_unset=True)

    # Delta detection: apply and log only fields that actually changed.
    changes: list[str] = []
    for key, value in data.items():
        current = getattr(quotation, key)
        current_cmp = str(current) if current is not None else None
        new_cmp = str(value) if value is not None else None
        if current_cmp != new_cmp:
            changes.append(f"{key}: {current_cmp or 'empty'} -> {new_cmp or 'empty'}")
            setattr(quotation, key, value)

    if changes:
        quotation.updated_at = utcnow()
        if "contact_id" in data:
            quote_service._snapshot_customer(  # noqa: SLF001
                db, quotation, quotation.customer_id, quotation.contact_id
            )
        db.add(quotation)
        quote_service.log_event(db, quotation, f"Updated {', '.join(changes)}"[:500], employee_id)
        db.commit()
    db.refresh(quotation)
    return _to_detail(db, quotation)


@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_delete")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    if quotation.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DRAFT quotations can be deleted",
        )
    for model in (
        ITQuotationItems,
        ITPaymentSchedule,
        ITQuotationStatusHistory,
        ITQuotationDocuments,
        ITQuotationNotes,
    ):
        rows = db.exec(select(model).where(model.quotation_id == quotation_id)).all()
        for row in rows:
            db.delete(row)
    terms = db.get(ITQuotationTerms, quotation_id)
    if terms:
        db.delete(terms)
    db.delete(quotation)
    db.commit()


# ----------------------------
# Items
# ----------------------------
@router.post("/{quotation_id}/items", response_model=ItQuotationDetail, status_code=status.HTTP_201_CREATED)
def add_item(
    quotation_id: int,
    payload: ItQuotationItemCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    count = len(db.exec(select(ITQuotationItems).where(ITQuotationItems.quotation_id == quotation_id)).all())
    item = quote_service.build_item(db, quotation_id, payload, sort_order=count)
    db.add(item)
    db.flush()
    quote_service.recalculate_totals(db, quotation)
    quote_service.log_event(db, quotation, f"Item '{item.name_snapshot}' added", employee_id)
    db.commit()
    db.refresh(quotation)
    return _to_detail(db, quotation)


@router.patch("/{quotation_id}/items/{item_id}", response_model=ItQuotationDetail)
def update_item(
    quotation_id: int,
    item_id: int,
    payload: ItQuotationItemUpdate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    item = db.get(ITQuotationItems, item_id)
    if not item or item.quotation_id != quotation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    data = payload.model_dump(exclude_unset=True)
    field_map = {"name": "name_snapshot", "description": "description_snapshot", "scope": "scope_snapshot"}

    # Delta detection: only touch and log when something actually changed.
    changed = False
    for key, value in data.items():
        target = field_map.get(key, key)
        current = getattr(item, target)
        current_cmp = str(current) if current is not None else None
        new_cmp = str(value) if value is not None else None
        if current_cmp != new_cmp:
            setattr(item, target, value)
            changed = True

    if changed:
        line = calculate_line(item.quantity, item.unit_price, item.discount_percent, item.tax_rate)
        for key, value in line.items():
            setattr(item, key, value)

        db.add(item)
        db.flush()
        quote_service.recalculate_totals(db, quotation)
        quote_service.log_event(db, quotation, f"Item '{item.name_snapshot}' updated", employee_id)
        db.commit()
    db.refresh(quotation)
    return _to_detail(db, quotation)


@router.delete("/{quotation_id}/items/{item_id}", response_model=ItQuotationDetail)
def delete_item(
    quotation_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    item = db.get(ITQuotationItems, item_id)
    if not item or item.quotation_id != quotation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item_name = item.name_snapshot
    db.delete(item)
    db.flush()
    quote_service.recalculate_totals(db, quotation)
    quote_service.log_event(db, quotation, f"Item '{item_name}' removed", employee_id)
    db.commit()
    db.refresh(quotation)
    return _to_detail(db, quotation)


@router.put("/{quotation_id}/items/reorder", response_model=ItQuotationDetail)
def reorder_items(
    quotation_id: int,
    payload: ItQuotationItemsReorder,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    items = db.exec(select(ITQuotationItems).where(ITQuotationItems.quotation_id == quotation_id)).all()
    by_id = {i.quotation_item_id: i for i in items}
    for order, item_id in enumerate(payload.item_ids):
        item = by_id.get(item_id)
        if item:
            item.sort_order = order
            db.add(item)
    db.commit()
    db.refresh(quotation)
    return _to_detail(db, quotation)


# ----------------------------
# Terms & payment schedule
# ----------------------------
@router.get("/{quotation_id}/terms", response_model=ItQuotationTermsPayload)
def get_terms(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    _get_quotation(db, tenant_id, quotation_id)
    terms = db.get(ITQuotationTerms, quotation_id)
    if not terms:
        return ItQuotationTermsPayload()
    return ItQuotationTermsPayload(**terms.model_dump(exclude={"quotation_id"}))


@router.put("/{quotation_id}/terms", response_model=ItQuotationTermsPayload)
def put_terms(
    quotation_id: int,
    payload: ItQuotationTermsPayload,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)

    # Delta detection: skip the write entirely when nothing changed.
    existing = db.get(ITQuotationTerms, quotation_id)
    existing_data = existing.model_dump(exclude={"quotation_id"}) if existing else {}
    if existing_data == payload.model_dump():
        return ItQuotationTermsPayload(**existing_data)

    terms = quote_service.replace_terms(db, quotation_id, payload)
    quote_service.log_event(db, quotation, "Terms & conditions updated", employee_id)
    db.commit()
    return ItQuotationTermsPayload(**terms.model_dump(exclude={"quotation_id"}))


@router.get("/{quotation_id}/payment-schedule", response_model=list[ItPaymentScheduleRead])
def get_payment_schedule(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    _get_quotation(db, tenant_id, quotation_id)
    return db.exec(
        select(ITPaymentSchedule)
        .where(ITPaymentSchedule.quotation_id == quotation_id)
        .order_by(ITPaymentSchedule.sequence_number)
    ).all()


@router.put("/{quotation_id}/payment-schedule", response_model=list[ItPaymentScheduleRead])
def put_payment_schedule(
    quotation_id: int,
    payload: list[ItPaymentScheduleEntry],
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)

    # Delta detection: compare against the stored schedule before replacing.
    existing_rows = db.exec(
        select(ITPaymentSchedule)
        .where(ITPaymentSchedule.quotation_id == quotation_id)
        .order_by(ITPaymentSchedule.sequence_number)
    ).all()

    def normalize(entry) -> tuple:
        return (
            entry.sequence_number,
            entry.description,
            float(entry.percentage) if entry.percentage is not None else None,
            float(entry.amount) if entry.amount is not None else None,
            entry.due_rule,
        )

    if [normalize(r) for r in existing_rows] == [normalize(e) for e in payload]:
        return existing_rows

    rows = quote_service.replace_payment_schedule(db, quotation_id, payload)
    quote_service.log_event(db, quotation, "Payment schedule updated", employee_id)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


# ----------------------------
# Actions
# ----------------------------
@router.post("/{quotation_id}/duplicate", response_model=ItQuotationDetail)
def duplicate_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_create")),
):
    source = _get_quotation(db, tenant_id, quotation_id)
    clone = quote_service.duplicate_quotation(db, source, created_by=employee_id)
    return _to_detail(db, clone)


@router.post("/{quotation_id}/change-status", response_model=ItQuotationRead)
def change_quotation_status(
    quotation_id: int,
    payload: ItQuotationStatusChange,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    quote_service.change_status(db, quotation, payload.status, changed_by=employee_id, notes=payload.notes)
    db.commit()
    db.refresh(quotation)
    return quotation


@router.post("/{quotation_id}/send", response_model=ItQuotationRead)
async def send_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    if quotation.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quotation in status {quotation.status} cannot be sent",
        )
    return await send_quotation_email(db, quotation, sent_by=employee_id)


@router.get("/{quotation_id}/history", response_model=list[ItStatusHistoryRead])
def get_status_history(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    _get_quotation(db, tenant_id, quotation_id)
    return db.exec(
        select(ITQuotationStatusHistory)
        .where(ITQuotationStatusHistory.quotation_id == quotation_id)
        .order_by(ITQuotationStatusHistory.changed_at.desc())
    ).all()


# ----------------------------
# Internal notes (many per quotation)
# ----------------------------
@router.get("/{quotation_id}/notes", response_model=list[ItQuotationNoteRead])
def list_notes(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    _get_quotation(db, tenant_id, quotation_id)
    return db.exec(
        select(ITQuotationNotes)
        .where(ITQuotationNotes.quotation_id == quotation_id)
        .order_by(ITQuotationNotes.created_at.desc())  # type: ignore[attr-defined]
    ).all()


@router.post("/{quotation_id}/notes", response_model=ItQuotationNoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    quotation_id: int,
    payload: ItQuotationNoteCreate,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    _get_quotation(db, tenant_id, quotation_id)
    note = ITQuotationNotes(
        quotation_id=quotation_id,
        note_text=payload.note_text,
        created_by=employee_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{quotation_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    quotation_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_edit")),
):
    _get_quotation(db, tenant_id, quotation_id)
    note = db.get(ITQuotationNotes, note_id)
    if not note or note.quotation_id != quotation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()


# ----------------------------
# PDF & documents
# ----------------------------
@router.post("/{quotation_id}/generate-pdf", response_model=ItQuotationDocumentRead)
def generate_pdf(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    employee_id: int | None = Depends(get_current_employee_id),
    _perm=Depends(require_module_permission("it_quotations", "can_export")),
):
    quotation = _get_quotation(db, tenant_id, quotation_id)
    document = generate_quotation_pdf(db, quotation, generated_by=employee_id)
    quote_service.log_event(db, quotation, f"PDF v{document.document_version} generated", employee_id)
    db.commit()
    return document


@router.get("/{quotation_id}/documents", response_model=list[ItQuotationDocumentRead])
def list_quotation_documents(
    quotation_id: int,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_tenant_id),
    _perm=Depends(require_module_permission("it_quotations", "can_view")),
):
    _get_quotation(db, tenant_id, quotation_id)
    return db.exec(
        select(ITQuotationDocuments)
        .where(ITQuotationDocuments.quotation_id == quotation_id)
        .order_by(ITQuotationDocuments.document_version.desc())
    ).all()
