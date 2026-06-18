from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import get_current_employee, get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from core.config import settings
from core.datetime_utils import utcnow
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
        emp = db.get(Employees, db_msg.user_id)
        if emp:
            user_obj = EmployeeSchema(
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                display_name=emp.display_name,
                title=emp.title,
            )
    except Exception:
        user_obj = None

    return TicketMessage(
        ticket_message_id=db_msg.ticket_message_id,
        ticket_id=db_msg.ticket_id,
        user=user_obj,
        message_txt=db_msg.message_txt,
        created_at=db_msg.created_at,
        updated_at=db_msg.updated_at,
        edited_at=db_msg.edited_at,
    )


@router.get("/tickets/{ticket_id}/messages", response_model=list[TicketMessage])
def list_messages_for_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    msgs = db.exec(
        select(TicketMessages).where(TicketMessages.ticket_id == ticket_id).order_by(TicketMessages.created_at)
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
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db_msg = TicketMessages(
        ticket_id=ticket_id,
        user_id=current_employee.employee_id,
        message_txt=payload.message_txt,
        created_at=utcnow(),
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)

    # Send notification
    if ticket.creator and ticket.creator.email:
        background_tasks.add_task(
            notify_ticket_message,
            ticket_id=ticket.ticket_id,
            ticket_title=ticket.title,
            message_id=db_msg.ticket_message_id,
            message_text=payload.message_txt or "",
            commenter_id=current_employee.employee_id,
            commenter_name=current_employee.display_name
            or f"{current_employee.first_name} {current_employee.last_name}",
            commenter_email=current_employee.email or "",
            ticket_creator_id=ticket.created_by,
            ticket_creator_email=ticket.creator.email,
            ticket_assigned_to_id=ticket.assigned_to,
            ticket_assigned_to_email=ticket.assignee.email if ticket.assignee else None,
            action_url=f"{settings.APP_URL}/tickets/{ticket.ticket_id}",
        )

    return message_to_schema(db_msg, db)


@router.patch("/messages/{message_id}", response_model=TicketMessage)
def update_message(
    message_id: int,
    payload: TicketMessageUpdate,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    current_employee_id = user_permissions["employee"]["employee_id"]
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")

    # Only creator or admin can edit
    is_creator = db_msg.user_id == current_employee_id
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("admin_actions", False)
    if not (is_creator or has_admin):
        raise HTTPException(status_code=403, detail="Not allowed to edit message")

    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(db_msg, k, v)
    db_msg.updated_at = utcnow()
    db_msg.edited_at = utcnow()
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
    current_employee_id = user_permissions["employee"]["employee_id"]
    db_msg = db.get(TicketMessages, message_id)
    if not db_msg:
        raise HTTPException(status_code=404, detail="Message not found")
    is_creator = db_msg.user_id == current_employee_id
    has_admin = False
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            has_admin = perm.get("permissions", {}).get("admin_actions", False)
    if not (is_creator or has_admin):
        raise HTTPException(status_code=403, detail="Not allowed to delete message")

    db.delete(db_msg)
    db.commit()
    return {"success": True, "message": "Message deleted"}
