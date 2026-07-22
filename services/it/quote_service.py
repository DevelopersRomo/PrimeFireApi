"""IT quotation domain logic: snapshots, totals, status transitions."""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.customers import CustomerAlternateContacts, Customers
from models.it.catalog import ITCatalogItems
from models.it.quotations import (
    IT_QUOTATION_STATUSES,
    IT_STATUS_TRANSITIONS,
    ITPaymentSchedule,
    ITQuotationItems,
    ITQuotations,
    ITQuotationStatusHistory,
    ITQuotationTerms,
)
from schemas.it.quotations import (
    ItPaymentScheduleEntry,
    ItQuotationCreate,
    ItQuotationItemCreate,
    ItQuotationTermsPayload,
)
from services.it.quote_calculator import calculate_line, calculate_totals, validate_payment_percentages
from services.it.quote_number_service import next_quotation_number


def customer_display_name(customer: Customers) -> str:
    if customer.company_name:
        return customer.company_name
    parts = [customer.first_name, customer.last_name]
    return " ".join(p for p in parts if p) or f"Customer #{customer.customer_id}"


def _snapshot_customer(db: Session, quotation: ITQuotations, customer_id: int, contact_id: int | None) -> None:
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    quotation.customer_name_snapshot = customer_display_name(customer)

    address = customer.primary_address
    if address:
        address_parts = [address.address_1, address.city, address.state, address.zip_code]
        quotation.customer_address_snapshot = ", ".join(p for p in address_parts if p) or None
    else:
        quotation.customer_address_snapshot = None

    if contact_id:
        contact = db.get(CustomerAlternateContacts, contact_id)
        if not contact or contact.customer_id != customer_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found for this customer")
        quotation.contact_name_snapshot = contact.name
        quotation.customer_email_snapshot = contact.email
    else:
        quotation.contact_name_snapshot = None
        quotation.customer_email_snapshot = customer.primary_email


def build_item(db: Session, quotation_id: int, payload: ItQuotationItemCreate, sort_order: int) -> ITQuotationItems:
    """Build a quotation item, snapshotting catalog data when linked."""
    catalog: ITCatalogItems | None = None
    if payload.catalog_item_id:
        catalog = db.get(ITCatalogItems, payload.catalog_item_id)
        if not catalog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")

    name = payload.name or (catalog.name if catalog else None)
    if not name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Item requires a name or a catalog_item_id",
        )

    item_type = payload.item_type or (catalog.item_type if catalog else "OTHER")
    billing_cycle = payload.billing_cycle or (catalog.billing_cycle if catalog else "ONE_TIME")
    unit = payload.unit or (catalog.unit if catalog else "EA")
    unit_price = payload.unit_price if payload.unit_price is not None else (catalog.unit_price if catalog else Decimal("0"))
    tax_rate = payload.tax_rate if payload.tax_rate is not None else (catalog.tax_rate if catalog else Decimal("0"))

    line = calculate_line(payload.quantity, unit_price, payload.discount_percent, tax_rate)

    return ITQuotationItems(
        quotation_id=quotation_id,
        catalog_item_id=payload.catalog_item_id,
        item_type=item_type,
        billing_cycle=billing_cycle,
        code_snapshot=catalog.code if catalog else None,
        name_snapshot=name,
        description_snapshot=payload.description or (catalog.description if catalog else None),
        scope_snapshot=payload.scope or (catalog.scope_template if catalog else None),
        quantity=payload.quantity,
        unit=unit,
        unit_price=unit_price,
        discount_percent=payload.discount_percent,
        tax_rate=tax_rate,
        term_months=payload.term_months,
        sort_order=payload.sort_order or sort_order,
        **line,
    )


def recalculate_totals(db: Session, quotation: ITQuotations) -> None:
    items = db.exec(select(ITQuotationItems).where(ITQuotationItems.quotation_id == quotation.quotation_id)).all()
    totals = calculate_totals(
        [
            {
                "billing_cycle": i.billing_cycle,
                "line_subtotal": i.line_subtotal,
                "line_discount": i.line_discount,
                "line_tax": i.line_tax,
            }
            for i in items
        ]
    )
    quotation.one_time_subtotal = totals["one_time_subtotal"]
    quotation.monthly_recurring_subtotal = totals["monthly_recurring_subtotal"]
    quotation.annual_recurring_subtotal = totals["annual_recurring_subtotal"]
    quotation.discount_total = totals["discount_total"]
    quotation.tax_total = totals["tax_total"]
    quotation.initial_total = totals["initial_total"]
    quotation.updated_at = datetime.utcnow()


def replace_terms(db: Session, quotation_id: int, payload: ItQuotationTermsPayload) -> ITQuotationTerms:
    terms = db.get(ITQuotationTerms, quotation_id)
    if terms:
        for key, value in payload.model_dump().items():
            setattr(terms, key, value)
    else:
        terms = ITQuotationTerms(quotation_id=quotation_id, **payload.model_dump())
    db.add(terms)
    return terms


def replace_payment_schedule(
    db: Session, quotation_id: int, entries: list[ItPaymentScheduleEntry]
) -> list[ITPaymentSchedule]:
    if not validate_payment_percentages([e.model_dump() for e in entries]):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Payment schedule percentages must add up to 100",
        )

    existing = db.exec(select(ITPaymentSchedule).where(ITPaymentSchedule.quotation_id == quotation_id)).all()
    for row in existing:
        db.delete(row)
    # Flush deletes before inserting; otherwise the unique index on
    # (quotation_id, sequence_number) rejects the replacement rows.
    db.flush()

    rows = [ITPaymentSchedule(quotation_id=quotation_id, **entry.model_dump()) for entry in entries]
    for row in rows:
        db.add(row)
    return rows


def log_event(
    db: Session,
    quotation: ITQuotations,
    action: str,
    changed_by: int | None = None,
) -> None:
    """Append an audit row for a non-status action (edit, item change, PDF, ...).

    Skips the insert when the immediately previous row is the same action within
    two minutes, so a chained Save Draft does not flood the history.
    """
    last = db.exec(
        select(ITQuotationStatusHistory)
        .where(ITQuotationStatusHistory.quotation_id == quotation.quotation_id)
        .order_by(ITQuotationStatusHistory.changed_at.desc())  # type: ignore[attr-defined]
    ).first()
    if (
        last
        and last.change_notes == action
        and last.new_status == quotation.status
        and (datetime.utcnow() - last.changed_at).total_seconds() < 120
    ):
        return

    db.add(
        ITQuotationStatusHistory(
            quotation_id=quotation.quotation_id,
            previous_status=quotation.status,
            new_status=quotation.status,
            changed_by=changed_by,
            change_notes=action,
        )
    )


def record_status_change(
    db: Session,
    quotation: ITQuotations,
    new_status: str,
    changed_by: int | None = None,
    notes: str | None = None,
) -> None:
    db.add(
        ITQuotationStatusHistory(
            quotation_id=quotation.quotation_id,
            previous_status=quotation.status,
            new_status=new_status,
            changed_by=changed_by,
            change_notes=notes,
        )
    )
    quotation.status = new_status
    quotation.updated_at = datetime.utcnow()
    now = datetime.utcnow()
    if new_status == "SENT":
        quotation.sent_at = now
    elif new_status == "ACCEPTED":
        quotation.accepted_at = now
    elif new_status == "REJECTED":
        quotation.rejected_at = now


def change_status(
    db: Session,
    quotation: ITQuotations,
    new_status: str,
    changed_by: int | None = None,
    notes: str | None = None,
) -> None:
    if new_status not in IT_QUOTATION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Unknown status '{new_status}'",
        )
    allowed = IT_STATUS_TRANSITIONS.get(quotation.status, ())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition {quotation.status} -> {new_status}",
        )
    record_status_change(db, quotation, new_status, changed_by, notes)


def create_quotation(
    db: Session,
    payload: ItQuotationCreate,
    tenant_id: int,
    created_by: int | None = None,
) -> ITQuotations:
    quotation = ITQuotations(
        tenant_id=tenant_id,
        customer_id=payload.customer_id,
        contact_id=payload.contact_id,
        quotation_number=next_quotation_number(db),
        status="DRAFT",
        quote_date=payload.quote_date,
        expiration_date=payload.expiration_date,
        currency=payload.currency,
        customer_name_snapshot="",
        visible_notes=payload.visible_notes,
        internal_notes=payload.internal_notes,
        template_id=payload.template_id,
        owner_employee_id=payload.owner_employee_id,
        created_by=created_by,
    )
    _snapshot_customer(db, quotation, payload.customer_id, payload.contact_id)

    db.add(quotation)
    db.flush()

    for index, item_payload in enumerate(payload.items):
        db.add(build_item(db, quotation.quotation_id, item_payload, sort_order=index))

    if payload.terms:
        replace_terms(db, quotation.quotation_id, payload.terms)
    if payload.payment_schedule:
        replace_payment_schedule(db, quotation.quotation_id, payload.payment_schedule)

    db.flush()
    recalculate_totals(db, quotation)
    db.add(
        ITQuotationStatusHistory(
            quotation_id=quotation.quotation_id,
            previous_status=None,
            new_status="DRAFT",
            changed_by=created_by,
            change_notes="Quotation created",
        )
    )

    db.commit()
    db.refresh(quotation)
    return quotation


def duplicate_quotation(db: Session, source: ITQuotations, created_by: int | None = None) -> ITQuotations:
    clone = ITQuotations(
        tenant_id=source.tenant_id,
        customer_id=source.customer_id,
        contact_id=source.contact_id,
        quotation_number=next_quotation_number(db),
        status="DRAFT",
        quote_date=source.quote_date,
        expiration_date=source.expiration_date,
        currency=source.currency,
        customer_name_snapshot=source.customer_name_snapshot,
        contact_name_snapshot=source.contact_name_snapshot,
        customer_email_snapshot=source.customer_email_snapshot,
        customer_address_snapshot=source.customer_address_snapshot,
        visible_notes=source.visible_notes,
        internal_notes=source.internal_notes,
        template_id=source.template_id,
        owner_employee_id=source.owner_employee_id,
        created_by=created_by,
    )
    db.add(clone)
    db.flush()

    items = db.exec(select(ITQuotationItems).where(ITQuotationItems.quotation_id == source.quotation_id)).all()
    for item in items:
        data = item.model_dump(exclude={"quotation_item_id", "quotation_id"})
        db.add(ITQuotationItems(quotation_id=clone.quotation_id, **data))

    terms = db.get(ITQuotationTerms, source.quotation_id)
    if terms:
        data = terms.model_dump(exclude={"quotation_id"})
        db.add(ITQuotationTerms(quotation_id=clone.quotation_id, **data))

    schedule = db.exec(select(ITPaymentSchedule).where(ITPaymentSchedule.quotation_id == source.quotation_id)).all()
    for entry in schedule:
        data = entry.model_dump(exclude={"payment_schedule_id", "quotation_id"})
        db.add(ITPaymentSchedule(quotation_id=clone.quotation_id, **data))

    db.flush()
    recalculate_totals(db, clone)
    db.add(
        ITQuotationStatusHistory(
            quotation_id=clone.quotation_id,
            previous_status=None,
            new_status="DRAFT",
            changed_by=created_by,
            change_notes=f"Duplicated from {source.quotation_number}",
        )
    )

    db.commit()
    db.refresh(clone)
    return clone
