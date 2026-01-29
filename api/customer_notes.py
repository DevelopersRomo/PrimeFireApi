from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone

from api.dependencies import get_current_employee, require_authentication
from bd.dependencies import get_db
from models.customers import Customers, CustomerNotes
from models.employees import Employees
from schemas.customers import CustomerNoteCreate, CustomerNoteUpdate, CustomerNote, CustomerEmployee

router = APIRouter()

def note_to_schema(db_note: CustomerNotes) -> CustomerNote:
    """Convert CustomerNotes model to CustomerNote schema."""
    return CustomerNote(
        CustomerNoteId=db_note.CustomerNoteId,
        CustomerId=db_note.CustomerId,
        NoteText=db_note.NoteText,
        CreatedAt=db_note.CreatedAt,
        UpdatedAt=db_note.UpdatedAt,
        CreatedBy=db_note.CreatedBy,
        creator=CustomerEmployee(
            EmployeeId=db_note.creator.EmployeeId,
            DisplayName=db_note.creator.DisplayName,
            Email=db_note.creator.Email,
            Title=db_note.creator.Title
        ) if db_note.creator else None
    )

@router.get("/customers/{customer_id}/notes", response_model=List[CustomerNote])
def get_customer_notes(
    customer_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Get all notes for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.CustomerId == customer_id)
        .order_by(CustomerNotes.CreatedAt.desc())
    ).all()

    return [note_to_schema(note) for note in notes]

@router.post("/customers/{customer_id}/notes", response_model=CustomerNote)
def create_customer_note(
    customer_id: int,
    note: CustomerNoteCreate,
    current_employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    """Create a new note for a customer."""
    customer = db.get(Customers, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_note = CustomerNotes(
        CustomerId=customer_id,
        NoteText=note.NoteText,
        CreatedBy=current_employee.EmployeeId,
        CreatedAt=datetime.now(timezone.utc)
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.CustomerNoteId == db_note.CustomerNoteId)
    ).first()

    return note_to_schema(db_note)

@router.patch("/customers/{customer_id}/notes/{note_id}", response_model=CustomerNote)
def update_customer_note(
    customer_id: int,
    note_id: int,
    note_update: CustomerNoteUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Update a customer note."""
    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(
            CustomerNotes.CustomerNoteId == note_id,
            CustomerNotes.CustomerId == customer_id
        )
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)

    db_note.UpdatedAt = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_note)

    db_note = db.exec(
        select(CustomerNotes)
        .options(selectinload(CustomerNotes.creator))
        .filter(CustomerNotes.CustomerNoteId == note_id)
    ).first()

    return note_to_schema(db_note)

@router.delete("/customers/{customer_id}/notes/{note_id}")
def delete_customer_note(
    customer_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Delete a customer note."""
    db_note = db.exec(
        select(CustomerNotes).filter(
            CustomerNotes.CustomerNoteId == note_id,
            CustomerNotes.CustomerId == customer_id
        )
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return {"success": True, "message": "Note deleted successfully"}
