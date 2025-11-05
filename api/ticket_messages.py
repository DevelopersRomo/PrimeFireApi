from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from bd.dependencies import get_db
from api.dependencies import get_current_employee, require_authentication, get_current_employee_with_permissions
from models.ticket_messages import TicketMessages
from models.employees import Employees
from schemas.ticket_messages import TicketMessageCreate, TicketMessageUpdate, TicketMessage
from schemas.employees import Employee as EmployeeSchema

router = APIRouter()


def message_to_schema(db_msg: TicketMessages, db: Session) -> TicketMessage:
    # Load employee and convert to schema
    user_obj = None
    try:
        emp = db.get(Employees, db_msg.UserId)
        if emp:
            user_obj = EmployeeSchema(
                EmployeeId=emp.EmployeeId,
                FirstName=emp.FirstName,
                LastName=emp.LastName,
                DisplayName=emp.DisplayName,
                Title=emp.Title,
            )
    except Exception:
        user_obj = None

    return TicketMessage(
        TicketMessageId=db_msg.TicketMessageId,
        TicketId=db_msg.TicketId,
        User=user_obj,
        MessageTxt=db_msg.MessageTxt,
        CreatedAt=db_msg.CreatedAt,
        UpdatedAt=db_msg.UpdatedAt,
        EditedAt=db_msg.EditedAt,
    )


@router.get("/tickets/{ticket_id}/messages", response_model=List[TicketMessage])
def list_messages_for_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    msgs = db.exec(select(TicketMessages).where(TicketMessages.TicketId == ticket_id).order_by(TicketMessages.CreatedAt)).all()
    return [message_to_schema(m, db) for m in msgs]


@router.get("/messages/{message_id}", response_model=TicketMessage)
def get_message(message_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return message_to_schema(db_msg, db)


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessage)
def create_message(ticket_id: int, payload: TicketMessageCreate, current_employee: Employees = Depends(get_current_employee), db: Session = Depends(get_db)):
    db_msg = TicketMessages(
        TicketId=ticket_id,
        UserId=current_employee.EmployeeId,
        MessageTxt=payload.MessageTxt,
        CreatedAt=datetime.now(timezone.utc)
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return message_to_schema(db_msg, db)


@router.patch("/messages/{message_id}", response_model=TicketMessage)
def update_message(message_id: int, payload: TicketMessageUpdate, user_permissions: dict = Depends(get_current_employee_with_permissions), db: Session = Depends(get_db)):
    current_employee_id = user_permissions["employee"]["EmployeeId"]
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only creator or admin can edit
    is_creator = db_msg.UserId == current_employee_id
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("AdminActions", False)
    if not (is_creator or has_admin):
        raise HTTPException(status_code=403, detail="Not allowed to edit message")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_msg, k, v)
    db_msg.UpdatedAt = datetime.now(timezone.utc)
    db_msg.EditedAt = datetime.now(timezone.utc)
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return message_to_schema(db_msg, db)


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, user_permissions: dict = Depends(get_current_employee_with_permissions), db: Session = Depends(get_db)):
    current_employee_id = user_permissions["employee"]["EmployeeId"]
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")
    is_creator = db_msg.UserId == current_employee_id
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("AdminActions", False)
    if not (is_creator or has_admin):
        raise HTTPException(status_code=403, detail="Not allowed to delete message")

    db.delete(db_msg)
    db.commit()
    return {"success": True, "message": "Message deleted"}
