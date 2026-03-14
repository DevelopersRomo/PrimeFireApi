from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
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
    CustomerMerged,
    CustomerNote,
    CustomerUpdate,
)

router = APIRouter()


def customer_to_schema(db_customer: Customers) -> Customer:
    """Convert Customers model to Customer schema with related data."""
    return Customer(
        CustomerId=db_customer.CustomerId,
        CustomerType=db_customer.CustomerType,
        CompanyName=db_customer.CompanyName,
        FirstName=db_customer.FirstName,
        LastName=db_customer.LastName,
        AdditionalName=db_customer.AdditionalName,
        Market=db_customer.Market,
        DtdPotential=db_customer.DtdPotential,
        PrimaryEmail=db_customer.PrimaryEmail,
        PrimaryPhone=db_customer.PrimaryPhone,
        PrimaryAddressId=db_customer.PrimaryAddressId,
        PrimaryAddress=AddressSchema(
            AddressId=db_customer.primary_address.AddressId,
            Address1=db_customer.primary_address.Address1,
            Address2=db_customer.primary_address.Address2,
            City=db_customer.primary_address.City,
            State=db_customer.primary_address.State,
            ZipCode=db_customer.primary_address.ZipCode,
            CountryId=db_customer.primary_address.CountryId,
            GooglePlaceId=db_customer.primary_address.GooglePlaceId,
            IsValidated=db_customer.primary_address.IsValidated,
            ValidatedAt=db_customer.primary_address.ValidatedAt,
            CreatedAt=db_customer.primary_address.CreatedAt,
        )
        if db_customer.primary_address
        else None,
        CreatedAt=db_customer.CreatedAt,
        UpdatedAt=db_customer.UpdatedAt,
        CreatedBy=db_customer.CreatedBy,
        creator=CustomerEmployee(
            EmployeeId=db_customer.creator.EmployeeId,
            DisplayName=db_customer.creator.DisplayName,
            Email=db_customer.creator.Email,
            Title=db_customer.creator.Title,
        )
        if db_customer.creator
        else None,
    )


@router.get("", response_model=list[Customer])
def get_customers(
    customer_type: CustomerTypeEnum | None = Query(None, description="Filter by customer type"),
    market: MarketEnum | None = Query(None, description="Filter by market"),
    dtd_potential: DtdPotentialEnum | None = Query(None, description="Filter by DTD potential"),
    search: str | None = Query(None, description="Search in name, company, email"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Get customers with optional filters and pagination."""
    query = select(Customers).options(selectinload(Customers.primary_address), selectinload(Customers.creator))

    filters = []
    if customer_type:
        filters.append(Customers.CustomerType == customer_type)
    if market:
        filters.append(Customers.Market == market)
    if dtd_potential:
        filters.append(Customers.DtdPotential == dtd_potential)
    if search:
        search_filter = f"%{search}%"
        filters.append(
            or_(
                Customers.CompanyName.ilike(search_filter),
                Customers.FirstName.ilike(search_filter),
                Customers.LastName.ilike(search_filter),
                Customers.PrimaryEmail.ilike(search_filter),
            )
        )

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Customers.CreatedAt.desc()).offset(skip).limit(limit)

    customers = db.exec(query).all()
    return [customer_to_schema(customer) for customer in customers]


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get a single customer by ID."""
    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.CustomerId == customer_id)
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
        .filter(Customers.CustomerId == customer_id)
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = [
        CustomerNote(
            CustomerNoteId=note.CustomerNoteId,
            CustomerId=note.CustomerId,
            NoteText=note.NoteText,
            CreatedAt=note.CreatedAt,
            UpdatedAt=note.UpdatedAt,
            CreatedBy=note.CreatedBy,
            creator=CustomerEmployee(
                EmployeeId=note.creator.EmployeeId,
                DisplayName=note.creator.DisplayName,
                Email=note.creator.Email,
                Title=note.creator.Title,
            )
            if note.creator
            else None,
        )
        for note in db_customer.notes
    ]

    contacts = [
        CustomerAlternateContact(
            CustomerAlternateContactId=contact.CustomerAlternateContactId,
            CustomerId=contact.CustomerId,
            Name=contact.Name,
            Email=contact.Email,
            Phone=contact.Phone,
            CreatedAt=contact.CreatedAt,
            UpdatedAt=contact.UpdatedAt,
        )
        for contact in db_customer.alternate_contacts
    ]

    attachments = [
        CustomerAttachment(
            CustomerAttachmentId=att.CustomerAttachmentId,
            CustomerId=att.CustomerId,
            FileName=att.FileName,
            FileType=att.FileType,
            FilePath=att.FilePath,
            CreatedAt=att.CreatedAt,
            CreatedBy=att.CreatedBy,
            creator=CustomerEmployee(
                EmployeeId=att.creator.EmployeeId,
                DisplayName=att.creator.DisplayName,
                Email=att.creator.Email,
                Title=att.creator.Title,
            )
            if att.creator
            else None,
        )
        for att in db_customer.attachments
    ]

    return CustomerMerged(
        Customer=customer_to_schema(db_customer), Notes=notes, Contacts=contacts, Attachments=attachments
    )


@router.post("", response_model=Customer)
def create_customer(
    customer: CustomerCreate, current_employee: Employees = Depends(get_current_employee), db: Session = Depends(get_db)
):
    """Create a new customer."""
    primary_address_id = None

    if customer.PrimaryAddress:
        db_address = Addresses(
            Address1=customer.PrimaryAddress.Address1,
            Address2=customer.PrimaryAddress.Address2,
            City=customer.PrimaryAddress.City,
            State=customer.PrimaryAddress.State,
            ZipCode=customer.PrimaryAddress.ZipCode,
            CountryId=customer.PrimaryAddress.CountryId,
            GooglePlaceId=customer.PrimaryAddress.GooglePlaceId,
        )
        db.add(db_address)
        db.flush()
        primary_address_id = db_address.AddressId
    elif customer.PrimaryAddressId:
        address_exists = db.get(Addresses, customer.PrimaryAddressId)
        if not address_exists:
            raise HTTPException(status_code=404, detail="Address not found")
        primary_address_id = customer.PrimaryAddressId

    db_customer = Customers(
        CustomerType=customer.CustomerType,
        CompanyName=customer.CompanyName,
        FirstName=customer.FirstName,
        LastName=customer.LastName,
        AdditionalName=customer.AdditionalName,
        Market=customer.Market,
        DtdPotential=customer.DtdPotential,
        PrimaryEmail=customer.PrimaryEmail,
        PrimaryPhone=customer.PrimaryPhone,
        PrimaryAddressId=primary_address_id,
        CreatedBy=current_employee.EmployeeId,
        CreatedAt=datetime.now(UTC),
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.CustomerId == db_customer.CustomerId)
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
        .filter(Customers.CustomerId == customer_id)
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = customer_update.model_dump(exclude_unset=True, exclude={"PrimaryAddress"})

    if customer_update.PrimaryAddress:
        if db_customer.PrimaryAddressId:
            db_address = db.get(Addresses, db_customer.PrimaryAddressId)
            if db_address:
                address_update = customer_update.PrimaryAddress.model_dump(exclude_unset=True)
                for key, value in address_update.items():
                    setattr(db_address, key, value)
        else:
            db_address = Addresses(
                Address1=customer_update.PrimaryAddress.Address1 or "",
                Address2=customer_update.PrimaryAddress.Address2,
                City=customer_update.PrimaryAddress.City or "",
                State=customer_update.PrimaryAddress.State or "",
                ZipCode=customer_update.PrimaryAddress.ZipCode or "",
                CountryId=customer_update.PrimaryAddress.CountryId or 0,
            )
            db.add(db_address)
            db.flush()
            update_data["PrimaryAddressId"] = db_address.AddressId

    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db_customer.UpdatedAt = datetime.now(UTC)
    db.commit()
    db.refresh(db_customer)

    db_customer = db.exec(
        select(Customers)
        .options(selectinload(Customers.primary_address), selectinload(Customers.creator))
        .filter(Customers.CustomerId == customer_id)
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
