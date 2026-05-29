from datetime import UTC, datetime
from core.datetime_utils import utcnow

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
        customer_alternate_contact_id=db_contact.customer_alternate_contact_id,
        customer_id=db_contact.customer_id,
        name=db_contact.name,
        email=db_contact.email,
        phone=db_contact.phone,
        created_at=db_contact.created_at,
        updated_at=db_contact.updated_at,
    )


@router.get("/customers/{customer_id}/contacts", response_model=list[CustomerAlternateContact])
def get_customer_contacts(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get all alternate contacts for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    contacts = db.exec(
        select(CustomerAlternateContacts)
        .filter(CustomerAlternateContacts.customer_id == customer_id)
        .order_by(CustomerAlternateContacts.created_at.desc())
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
        customer_id=customer_id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        created_at=utcnow(),
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
            CustomerAlternateContacts.customer_alternate_contact_id == contact_id,
            CustomerAlternateContacts.customer_id == customer_id,
        )
    ).first()

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_contact, key, value)

    db_contact.updated_at = utcnow()
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
            CustomerAlternateContacts.customer_alternate_contact_id == contact_id,
            CustomerAlternateContacts.customer_id == customer_id,
        )
    ).first()

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()
    return {"success": True, "message": "Contact deleted successfully"}
