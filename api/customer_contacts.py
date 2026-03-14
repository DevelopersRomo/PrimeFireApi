from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.customers import CustomerAlternateContacts, Customers
from schemas.customers import CustomerAlternateContact, CustomerAlternateContactCreate, CustomerAlternateContactUpdate

router = APIRouter()


def contact_to_schema(db_contact: CustomerAlternateContacts) -> CustomerAlternateContact:
    """Convert CustomerAlternateContacts model to CustomerAlternateContact schema."""
    return CustomerAlternateContact(
        CustomerAlternateContactId=db_contact.CustomerAlternateContactId,
        CustomerId=db_contact.CustomerId,
        Name=db_contact.Name,
        Email=db_contact.Email,
        Phone=db_contact.Phone,
        CreatedAt=db_contact.CreatedAt,
        UpdatedAt=db_contact.UpdatedAt,
    )


@router.get("/customers/{customer_id}/contacts", response_model=list[CustomerAlternateContact])
def get_customer_contacts(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get all alternate contacts for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    contacts = db.exec(
        select(CustomerAlternateContacts)
        .filter(CustomerAlternateContacts.CustomerId == customer_id)
        .order_by(CustomerAlternateContacts.CreatedAt.desc())
    ).all()

    return [contact_to_schema(contact) for contact in contacts]


@router.post("/customers/{customer_id}/contacts", response_model=CustomerAlternateContact)
def create_customer_contact(
    customer_id: int,
    contact: CustomerAlternateContactCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Create a new alternate contact for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_contact = CustomerAlternateContacts(
        CustomerId=customer_id,
        Name=contact.Name,
        Email=contact.Email,
        Phone=contact.Phone,
        CreatedAt=datetime.now(UTC),
    )

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)

    return contact_to_schema(db_contact)


@router.patch("/customers/{customer_id}/contacts/{contact_id}", response_model=CustomerAlternateContact)
def update_customer_contact(
    customer_id: int,
    contact_id: int,
    contact_update: CustomerAlternateContactUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Update a customer alternate contact."""
    db_contact = db.exec(
        select(CustomerAlternateContacts).filter(
            CustomerAlternateContacts.CustomerAlternateContactId == contact_id,
            CustomerAlternateContacts.CustomerId == customer_id,
        )
    ).first()

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_contact, key, value)

    db_contact.UpdatedAt = datetime.now(UTC)
    db.commit()
    db.refresh(db_contact)

    return contact_to_schema(db_contact)


@router.delete("/customers/{customer_id}/contacts/{contact_id}")
def delete_customer_contact(
    customer_id: int, contact_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """Delete a customer alternate contact."""
    db_contact = db.exec(
        select(CustomerAlternateContacts).filter(
            CustomerAlternateContacts.CustomerAlternateContactId == contact_id,
            CustomerAlternateContacts.CustomerId == customer_id,
        )
    ).first()

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()
    return {"success": True, "message": "Contact deleted successfully"}
