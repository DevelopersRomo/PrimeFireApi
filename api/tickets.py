from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, and_, or_, select

from api.dependencies import get_current_employee, get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from core.config import settings
from models.employees import Employees
from models.tickets import TicketPriority, TicketSLA, TicketStatus, Tickets
from schemas.tickets import Ticket, TicketCreate, TicketEmployee, TicketUpdate
from services.notifications.notifications import (
    notify_ticket_created,
    send_ticket_assigned_notification,
)
from services.notifications.schemas import TicketNotificationData

router = APIRouter()


def has_admin_actions(user_permissions: dict) -> bool:
    """Check if user has AdminActions permission for tickets module."""
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            return perm.get("permissions", {}).get("AdminActions", False)
    return False


def ticket_to_schema(db_ticket: Tickets) -> Ticket:
    """Convert Tickets model to Ticket schema with related employee data."""
    return Ticket(
        TicketId=db_ticket.TicketId,
        Title=db_ticket.Title,
        Description=db_ticket.Description,
        Status=db_ticket.Status,
        Priority=db_ticket.Priority,
        SLA=db_ticket.SLA,
        CreatedBy=db_ticket.CreatedBy,
        AssignedTo=db_ticket.AssignedTo,
        CreatedAt=db_ticket.CreatedAt,
        UpdatedAt=db_ticket.UpdatedAt,
        creator=TicketEmployee(
            EmployeeId=db_ticket.creator.EmployeeId,
            DisplayName=db_ticket.creator.DisplayName,
            Email=db_ticket.creator.Email,
            Title=db_ticket.creator.Title,
        )
        if db_ticket.creator
        else None,
        assignee=TicketEmployee(
            EmployeeId=db_ticket.assignee.EmployeeId,
            DisplayName=db_ticket.assignee.DisplayName,
            Email=db_ticket.assignee.Email,
            Title=db_ticket.assignee.Title,
        )
        if db_ticket.assignee
        else None,
    )


# ----------------------------
# 📌 GET /tickets (LIST WITH FILTERS AND PAGINATION)
# ----------------------------
@router.get("", response_model=list[Ticket])
def get_tickets(
    # Filters
    status: TicketStatus | None = Query(None, description="Filter by ticket status"),
    priority: TicketPriority | None = Query(None, description="Filter by ticket priority"),
    sla: TicketSLA | None = Query(None, description="Filter by service level agreement"),
    assigned_to: int | None = Query(None, description="Filter by assigned employee ID"),
    created_by: int | None = Query(None, description="Filter by creator employee ID"),
    search: str | None = Query(None, description="Search in title and description"),
    # Pagination
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Get tickets with optional filters and pagination."""
    # Build base query with relationships
    query = select(Tickets).options(selectinload(Tickets.creator), selectinload(Tickets.assignee))

    # Apply filters
    filters = []
    if status:
        filters.append(Tickets.Status == status)
    if priority:
        filters.append(Tickets.Priority == priority)
    if sla:
        filters.append(sla == Tickets.SLA)
    if assigned_to:
        filters.append(Tickets.AssignedTo == assigned_to)
    if created_by:
        filters.append(Tickets.CreatedBy == created_by)
    if search:
        search_filter = f"%{search}%"
        filters.append(or_(Tickets.Title.ilike(search_filter), Tickets.Description.ilike(search_filter)))

    if filters:
        query = query.where(and_(*filters))

    # Apply ordering (newest first) and pagination
    query = query.order_by(Tickets.CreatedAt.desc()).offset(skip).limit(limit)

    tickets = db.exec(query).all()
    return [ticket_to_schema(ticket) for ticket in tickets]


# ----------------------------
# 📌 GET /tickets/{id} (GET SINGLE TICKET)
# ----------------------------
@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get a single ticket by ID."""
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket_to_schema(db_ticket)


# ----------------------------
# 📌 POST /tickets (CREATE TICKET)
# ----------------------------
@router.post("", response_model=Ticket)
def create_ticket(
    ticket: TicketCreate,
    background_tasks: BackgroundTasks,
    current_employee: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    """Create a new ticket. Creator is automatically set to the authenticated user."""
    # Validate assigned employee exists if provided
    if ticket.AssignedTo:
        assigned_employee = db.exec(select(Employees).filter(Employees.EmployeeId == ticket.AssignedTo)).first()
        if not assigned_employee:
            raise HTTPException(status_code=404, detail="Assigned employee not found")

    # Create ticket
    db_ticket = Tickets(
        Title=ticket.Title,
        Description=ticket.Description,
        Status=ticket.Status,
        Priority=ticket.Priority,
        SLA=ticket.SLA,
        CreatedBy=current_employee.EmployeeId,
        AssignedTo=ticket.AssignedTo,
        CreatedAt=datetime.now(UTC),
        UpdatedAt=datetime.now(UTC),
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    # Load relationships for response
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == db_ticket.TicketId)
    ).first()

    # Send notification if ticket has assignee and assignee is different from creator
    if db_ticket.AssignedTo and db_ticket.assignee and db_ticket.AssignedTo != current_employee.EmployeeId:
        background_tasks.add_task(
            notify_ticket_created,
            ticket_id=db_ticket.TicketId,
            title=db_ticket.Title,
            description=db_ticket.Description,
            status=db_ticket.Status.value,
            priority=db_ticket.Priority.value,
            created_by_name=db_ticket.creator.DisplayName
            or f"{db_ticket.creator.FirstName} {db_ticket.creator.LastName}",
            created_by_email=db_ticket.creator.Email or "",
            assigned_to_name=db_ticket.assignee.DisplayName
            or f"{db_ticket.assignee.FirstName} {db_ticket.assignee.LastName}",
            assigned_to_email=db_ticket.assignee.Email or "",
            action_url=f"{settings.APP_URL}/tickets/{db_ticket.TicketId}",
            notify_assignee=True,
        )

    return ticket_to_schema(db_ticket)


# ----------------------------
# 📌 PATCH /tickets/{id} (UPDATE TICKET)
# ----------------------------
@router.patch("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    background_tasks: BackgroundTasks,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Update a ticket. Only creator, assigned employee, or users with AdminActions can update."""
    current_employee_id = user_permissions["employee"]["EmployeeId"]

    # Get ticket
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check permissions: creator, assignee, or AdminActions
    is_creator = db_ticket.CreatedBy == current_employee_id
    is_assignee = db_ticket.AssignedTo == current_employee_id
    has_admin = has_admin_actions(user_permissions)

    if not (is_creator or is_assignee or has_admin):
        raise HTTPException(
            status_code=403,
            detail="You can only update tickets you created, are assigned to, or have admin permissions",
        )

    # Track if AssignedTo changed
    old_assigned_to = db_ticket.AssignedTo

    # Validate assigned employee exists if being updated
    if ticket_update.AssignedTo is not None and ticket_update.AssignedTo:  # If assigning to someone
        assigned_employee = db.exec(select(Employees).filter(Employees.EmployeeId == ticket_update.AssignedTo)).first()
        if not assigned_employee:
            raise HTTPException(status_code=404, detail="Assigned employee not found")

    # Apply updates
    update_data = ticket_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)

    # Update timestamp
    db_ticket.UpdatedAt = datetime.now(UTC)

    db.commit()
    db.refresh(db_ticket)

    # Reload relationships after update
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == ticket_id)
    ).first()

    # Send notification if AssignedTo changed and new assignee exists and is different from current user
    if ticket_update.AssignedTo is not None and old_assigned_to != db_ticket.AssignedTo:  # noqa: SIM102
        if db_ticket.AssignedTo and db_ticket.assignee and db_ticket.AssignedTo != current_employee_id:
            notification_data = TicketNotificationData(
                ticket_id=db_ticket.TicketId,
                title=db_ticket.Title,
                description=db_ticket.Description,
                status=db_ticket.Status.value,
                priority=db_ticket.Priority.value,
                created_by_name=db_ticket.creator.DisplayName
                or f"{db_ticket.creator.FirstName} {db_ticket.creator.LastName}",
                created_by_email=db_ticket.creator.Email or "",
                assigned_to_name=db_ticket.assignee.DisplayName
                or f"{db_ticket.assignee.FirstName} {db_ticket.assignee.LastName}",
                assigned_to_email=db_ticket.assignee.Email or "",
                action_url=f"{settings.APP_URL}/tickets/{db_ticket.TicketId}",
            )
            background_tasks.add_task(
                send_ticket_assigned_notification,
                notification_data=notification_data,
                to_email=db_ticket.assignee.Email or "",
            )

    return ticket_to_schema(db_ticket)


# ----------------------------
# 📌 DELETE /tickets/{id} (SOFT DELETE - MARK AS CLOSED)
# ----------------------------
@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Soft delete a ticket by marking it as closed. Only creator or users with AdminActions can delete."""
    current_employee_id = user_permissions["employee"]["EmployeeId"]

    # Get ticket
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.TicketId == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check permissions: creator or AdminActions
    is_creator = db_ticket.CreatedBy == current_employee_id
    has_admin = has_admin_actions(user_permissions)

    if not (is_creator or has_admin):
        raise HTTPException(
            status_code=403, detail="Only the ticket creator or users with admin permissions can delete it"
        )

    # Delete the ticket from the database
    db.delete(db_ticket)
    db.commit()
    return {"success": True, "message": "Ticket deleted successfully"}
