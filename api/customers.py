from datetime import UTC, datetime
from core.datetime_utils import utcnow

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, and_, or_, select

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
from models.addresses import Addresses
from models.customers import (
    CustomerAttachments,
    CustomerNotes,
    CustomerTypeEnum,
    Customers,
    DtdPotentialEnum,
    MarketEnum,
)
from models.employees import Employees
from schemas.customers import (
    Address as AddressSchema,
)
from schemas.customers import (
    Customer,
    CustomerAlternateContact,
    CustomerAttachment,
    CustomerCreate,
    CustomerEmployee,
    CustomerListResponse,
    CustomerMerged,
    CustomerNote,
    CustomerUpdate,
)

router = APIRouter()


def customer_to_schema(db_customer: Customers) -> Customer:
    """Convert Customers model to Customer schema with related data."""
    return Customer(
        customer_id=db_customer.customer_id,
        customer_type=db_customer.customer_type,
        company_name=db_customer.company_name,
        first_name=db_customer.first_name,
        last_name=db_customer.last_name,
        additional_name=db_customer.additional_name,
        market=db_customer.market,
        dtd_potential=db_customer.dtd_potential,
        primary_email=db_customer.primary_email,
        primary_phone=db_customer.primary_phone,
        primary_address_id=db_customer.primary_address_id,
        primary_address=AddressSchema(
            address_id=db_customer.primary_address.address_id,
            address_1=db_customer.primary_address.address_1,
            address_2=db_customer.primary_address.address_2,
            city=db_customer.primary_address.city,
            state=db_customer.primary_address.state,
            zip_code=db_customer.primary_address.zip_code,
            country_id=db_customer.primary_address.country_id,
            google_place_id=db_customer.primary_address.google_place_id,
            is_validated=db_customer.primary_address.is_validated,
            validated_at=db_customer.primary_address.validated_at,
            created_at=db_customer.primary_address.created_at,
        )
        if db_customer.primary_address
        else None,
        created_at=db_customer.created_at,
        updated_at=db_customer.updated_at,
        created_by=db_customer.created_by,
        creator=CustomerEmployee(
            employee_id=db_customer.creator.employee_id,
            display_name=db_customer.creator.display_name,
            email=db_customer.creator.email,
            title=db_customer.creator.title,
        )
        if db_customer.creator
        else None,
    )


@router.get("", response_model=list[Customer] | CustomerListResponse)
def get_customers(
    customer_type: CustomerTypeEnum | None = Query(None, description="Filter by customer type"),
    market: MarketEnum | None = Query(None, description="Filter by market"),
    dtd_potential: DtdPotentialEnum | None = Query(None, description="Filter by DTD potential"),
    search: str | None = Query(None, description="Search in name, company, email"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of records to return"),
    with_meta: bool = Query(False, description="Return pagination metadata"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Get customers with optional filters and pagination."""
    query = select(Customers).options(selectinload(Customers.primary_address), selectinload(Customers.creator))

    filters = []
    if customer_type:
        filters.append(Customers.customer_type == customer_type)
    if market:
        filters.append(Customers.market == market)
    if dtd_potential:
        filters.append(Customers.dtd_potential == dtd_potential)
    if search:
        search_filter = f"%{search}%"
        filters.append(
            or_(
                Customers.company_name.ilike(search_filter),
                Customers.first_name.ilike(search_filter),
                Customers.last_name.ilike(search_filter),
                Customers.primary_email.ilike(search_filter),
            )
        )

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Customers.created_at.desc()).offset(skip).limit(limit)

    customers = db.exec(query).all()
    items = [customer_to_schema(customer) for customer in customers]

    if not with_meta:
        return items

    count_query = select(func.count()).select_from(Customers)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = db.exec(count_query).one()
    total = total_result if isinstance(total_result, int) else total_result[0]

    return CustomerListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get a single customer by ID."""
    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.customer_id == customer_id)
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer_to_schema(db_customer)


@router.get("/{customer_id}/merged", response_model=CustomerMerged)
def get_customer_merged(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get a customer with notes, contacts, and attachments."""
    db_customer = db.exec(
        select(Customers)
        .options(
            selectinload(Customers.primary_address),
            selectinload(Customers.creator),
            selectinload(Customers.notes).selectinload(CustomerNotes.creator),
            selectinload(Customers.alternate_contacts),
            selectinload(Customers.attachments).selectinload(CustomerAttachments.creator),
        )
        .filter(Customers.customer_id == customer_id)
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = [
        CustomerNote(
            customer_note_id=note.customer_note_id,
            customer_id=note.customer_id,
            note_text=note.note_text,
            created_at=note.created_at,
            updated_at=note.updated_at,
            created_by=note.created_by,
            creator=CustomerEmployee(
                employee_id=note.creator.employee_id,
                display_name=note.creator.display_name,
                email=note.creator.email,
                title=note.creator.title,
            )
            if note.creator
            else None,
        )
        for note in db_customer.notes
    ]

    contacts = [
        CustomerAlternateContact(
            customer_alternate_contact_id=contact.customer_alternate_contact_id,
            customer_id=contact.customer_id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )
        for contact in db_customer.alternate_contacts
    ]

    attachments = [
        CustomerAttachment(
            customer_attachment_id=att.customer_attachment_id,
            customer_id=att.customer_id,
            file_name=att.file_name,
            file_type=att.file_type,
            file_path=att.file_path,
            created_at=att.created_at,
            created_by=att.created_by,
            creator=CustomerEmployee(
                employee_id=att.creator.employee_id,
                display_name=att.creator.display_name,
                email=att.creator.email,
                title=att.creator.title,
            )
            if att.creator
            else None,
        )
        for att in db_customer.attachments
    ]

    return CustomerMerged(
        customer=customer_to_schema(db_customer), notes=notes, contacts=contacts, attachments=attachments
    )


@router.post("", response_model=Customer)
def create_customer(
    customer: CustomerCreate, current_employee: Employees = Depends(get_current_employee), db: Session = Depends(get_db)
):
    """Create a new customer."""
    primary_address_id = None

    if customer.primary_address:
        db_address = Addresses(
            address_1=customer.primary_address.address_1,
            address_2=customer.primary_address.address_2,
            city=customer.primary_address.city,
            state=customer.primary_address.state,
            zip_code=customer.primary_address.zip_code,
            country_id=customer.primary_address.country_id,
            google_place_id=customer.primary_address.google_place_id,
        )
        db.add(db_address)
        db.flush()
        primary_address_id = db_address.address_id
    elif customer.primary_address_id:
        address_exists = db.get(Addresses, customer.primary_address_id)
        if not address_exists:
            raise HTTPException(status_code=404, detail="Address not found")
        primary_address_id = customer.primary_address_id

    db_customer = Customers(
        customer_type=customer.customer_type,
        company_name=customer.company_name,
        first_name=customer.first_name,
        last_name=customer.last_name,
        additional_name=customer.additional_name,
        market=customer.market,
        dtd_potential=customer.dtd_potential,
        primary_email=customer.primary_email,
        primary_phone=customer.primary_phone,
        primary_address_id=primary_address_id,
        created_by=current_employee.employee_id,
        created_at=utcnow(),
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.customer_id == db_customer.customer_id)
    ).first()

    return customer_to_schema(db_customer)


@router.patch("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Update a customer."""
    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.customer_id == customer_id)
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = customer_update.model_dump(exclude_unset=True, exclude={"primary_address"})

    if customer_update.primary_address:
        if db_customer.primary_address_id:
            db_address = db.get(Addresses, db_customer.primary_address_id)
            if db_address:
                address_update = customer_update.primary_address.model_dump(exclude_unset=True)
                for key, value in address_update.items():
                    setattr(db_address, key, value)
        else:
            db_address = Addresses(
                address_1=customer_update.primary_address.address_1 or "",
                address_2=customer_update.primary_address.address_2,
                city=customer_update.primary_address.city or "",
                state=customer_update.primary_address.state or "",
                zip_code=customer_update.primary_address.zip_code or "",
                country_id=customer_update.primary_address.country_id or 0,
            )
            db.add(db_address)
            db.flush()
            update_data["primary_address_id"] = db_address.address_id

    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db_customer.updated_at = utcnow()
    db.commit()
    db.refresh(db_customer)

    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.customer_id == customer_id)
    ).first()

    return customer_to_schema(db_customer)


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Delete a customer."""
    db_customer = db.get(Customers, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(db_customer)
    db.commit()
    return {"success": True, "message": "Customer deleted successfully"}
