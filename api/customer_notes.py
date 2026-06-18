from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from models.customers import CustomerNotes, Customers
from models.employees import Employees
from schemas.customers import CustomerEmployee, CustomerNote, CustomerNoteCreate, CustomerNoteUpdate

router = APIRouter()


def note_to_schema(db_note: CustomerNotes) -> CustomerNote:
    """Convert CustomerNotes model to CustomerNote schema."""
    return CustomerNote(
        customer_note_id=db_note.customer_note_id,
        customer_id=db_note.customer_id,
        note_text=db_note.note_text,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at,
        created_by=db_note.created_by,
        creator=CustomerEmployee(
            employee_id=db_note.creator.employee_id,
            display_name=db_note.creator.display_name,
            email=db_note.creator.email,
            title=db_note.creator.title,
        )
        if db_note.creator
        else None,
    )


@router.get("/customers/{customer_id}/notes", response_model=list[CustomerNote])
def get_customer_notes(customer_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get all notes for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.customer_id == customer_id)
        .order_by(CustomerNotes.created_at.desc())
    ).all()

    return [note_to_schema(note) for note in notes]


@router.post("/customers/{customer_id}/notes", response_model=CustomerNote)
def create_customer_note(
    customer_id: int,
    note: CustomerNoteCreate,
    current_employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    """Create a new note for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_note = CustomerNotes(
        customer_id=customer_id,
        note_text=note.note_text,
        created_by=current_employee.employee_id,
        created_at=utcnow(),
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.customer_note_id == db_note.customer_note_id)
    ).first()

    return note_to_schema(db_note)


@router.patch("/customers/{customer_id}/notes/{note_id}", response_model=CustomerNote)
def update_customer_note(
    customer_id: int,
    note_id: int,
    note_update: CustomerNoteUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Update a customer note."""
    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.customer_note_id == note_id, CustomerNotes.customer_id == customer_id)
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)

    db_note.updated_at = utcnow()
    db.commit()
    db.refresh(db_note)

    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.customer_note_id == note_id)
    ).first()

    return note_to_schema(db_note)


@router.delete("/customers/{customer_id}/notes/{note_id}")
def delete_customer_note(
    customer_id: int, note_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """Delete a customer note."""
    db_note = db.exec(
        select(CustomerNotes).filter(
            CustomerNotes.customer_note_id == note_id, CustomerNotes.customer_id == customer_id
        )
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return {"success": True, "message": "Note deleted successfully"}
