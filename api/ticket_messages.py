from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee, get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from core.config import settings
from models.employees import Employees
from models.ticket_messages import TicketMessages
from models.tickets import Tickets
from schemas.employees import Employee as EmployeeSchema
from schemas.ticket_messages import TicketMessage, TicketMessageCreate, TicketMessageUpdate
from services.notifications.notifications import notify_ticket_message

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


@router.get("/tickets/{ticket_id}/messages", response_model=list[TicketMessage])
def list_messages_for_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    msgs = db.exec(
        select(TicketMessages).where(TicketMessages.TicketId == ticket_id).order_by(TicketMessages.CreatedAt)
    ).all()
    return [message_to_schema(m, db) for m in msgs]


@router.get("/messages/{message_id}", response_model=TicketMessage)
def get_message(message_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return message_to_schema(db_msg, db)


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessage)
def create_message(
    ticket_id: int,
    payload: TicketMessageCreate,
    background_tasks: BackgroundTasks,
    current_employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    # Get ticket with relationships
    ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == ticket_id)
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db_msg = TicketMessages(
        TicketId=ticket_id,
        UserId=current_employee.EmployeeId,
        MessageTxt=payload.MessageTxt,
        CreatedAt=datetime.now(UTC),
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)

    # Send notification
    if ticket.creator and ticket.creator.Email:
        background_tasks.add_task(
            notify_ticket_message,
            ticket_id=ticket.TicketId,
            ticket_title=ticket.Title,
            message_id=db_msg.TicketMessageId,
            message_text=payload.MessageTxt or "",
            commenter_id=current_employee.EmployeeId,
            commenter_name=current_employee.DisplayName or f"{current_employee.FirstName} {current_employee.LastName}",
            commenter_email=current_employee.Email or "",
            ticket_creator_id=ticket.CreatedBy,
            ticket_creator_email=ticket.creator.Email,
            ticket_assigned_to_id=ticket.AssignedTo,
            ticket_assigned_to_email=ticket.assignee.Email if ticket.assignee else None,
            action_url=f"{settings.APP_URL}/tickets/{ticket.TicketId}",
        )

    return message_to_schema(db_msg, db)


@router.patch("/messages/{message_id}", response_model=TicketMessage)
def update_message(
    message_id: int,
    payload: TicketMessageUpdate,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
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
    db_msg.UpdatedAt = datetime.now(UTC)
    db_msg.EditedAt = datetime.now(UTC)
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return message_to_schema(db_msg, db)


@router.delete("/messages/{message_id}")
def delete_message(
    message_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
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
