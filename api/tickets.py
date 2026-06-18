import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, and_, or_, select

from core.datetime_utils import utcnow

logger = logging.getLogger(__name__)

from api.dependencies import get_current_employee_with_permissions, require_authentication
from bd.dependencies import get_db
from core.config import settings
from models.employees import Employees
from models.tickets import (
    TicketPriority,
    TicketRecurrenceConfig,
    TicketRecurrenceType,
    TicketSLA,
    TicketStatus,
    Tickets,
)
from schemas.pagination import PaginatedResponse
from schemas.tickets import Ticket, TicketCreate, TicketEmployee, TicketUpdate
from services.notifications.notifications import (
    notify_ticket_created,
    send_ticket_assigned_notification,
)
from services.notifications.schemas import TicketNotificationData

router = APIRouter()


def _calculate_next_occurrence(from_date: datetime, recurrence_type: TicketRecurrenceType) -> datetime:
    """Calculate the next occurrence date based on recurrence type."""
    if recurrence_type == TicketRecurrenceType.DAILY:
        return from_date + relativedelta(days=1)
    if recurrence_type == TicketRecurrenceType.WEEKLY:
        return from_date + relativedelta(weeks=1)
    if recurrence_type == TicketRecurrenceType.BIWEEKLY:
        return from_date + relativedelta(weeks=2)
    if recurrence_type == TicketRecurrenceType.TRIWEEKLY:
        return from_date + relativedelta(weeks=3)
    if recurrence_type == TicketRecurrenceType.MONTHLY:
        return from_date + relativedelta(months=1)
    if recurrence_type == TicketRecurrenceType.BIMONTHLY:
        return from_date + relativedelta(months=2)
    if recurrence_type == TicketRecurrenceType.YEARLY:
        return from_date + relativedelta(years=1)
    return from_date


def has_admin_actions(user_permissions: dict) -> bool:
    """Check if user has admin_actions permission for tickets module."""
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            return perm.get("permissions", {}).get("admin_actions", False)
    return False


def get_subordinate_ids(manager_id: int, db: Session) -> list[int]:
    """Return all subordinate employee IDs (direct + indirect) for a manager.

    Recursively collects employees whose manager_employee_id points to the manager
    or any of their subordinates. Uses breadth-first traversal with a single query
    per level (typical org depth ≤3).
    """
    result: set[int] = set()
    to_process = {manager_id}

    while to_process:
        current_batch = list(to_process)
        to_process.clear()

        for current in current_batch:
            rows = db.exec(select(Employees.employee_id).where(Employees.manager_employee_id == current)).all()
            for emp_id in rows:
                if emp_id not in result:
                    result.add(emp_id)
                    to_process.add(emp_id)

    return list(result)


def get_ticket_visibility_scope(user_permissions: dict, db: Session) -> dict:
    """Return visibility scope for the current employee.

    Returns {'scope': 'admin'|'manager'|'user', 'allowed_ids': set[int]}.
    - admin: has admin_actions on tickets module → empty allowed_ids (no filter needed)
    - manager: has subordinates via manager_employee_id → self + all subordinates
    - user: neither admin nor manager → self only
    """
    employee_id = user_permissions["employee"]["employee_id"]

    if has_admin_actions(user_permissions):
        return {"scope": "admin", "allowed_ids": set()}

    subordinate_ids = get_subordinate_ids(employee_id, db)
    allowed_ids = {employee_id}

    if subordinate_ids:
        allowed_ids.update(subordinate_ids)
        return {"scope": "manager", "allowed_ids": allowed_ids}

    return {"scope": "user", "allowed_ids": allowed_ids}


def get_assignable_employee_ids(user_permissions: dict, db: Session) -> set[int]:
    """Return set of employee IDs the caller can assign tickets to.

    - admin: all employees
    - manager: self + all subordinates (BFS via get_subordinate_ids)
    - user: employees where department == 'IT'
    """
    if has_admin_actions(user_permissions):
        rows = db.exec(select(Employees.employee_id)).all()
        return set(rows)

    employee_id = user_permissions["employee"]["employee_id"]
    subordinate_ids = get_subordinate_ids(employee_id, db)

    if subordinate_ids:
        return {employee_id} | set(subordinate_ids)

    rows = db.exec(select(Employees.employee_id).where(Employees.department == "IT")).all()
    return set(rows)


def ticket_to_schema(db_ticket: Tickets) -> Ticket:
    """Convert Tickets model to Ticket schema with related employee data."""
    recurrence_type: TicketRecurrenceType | None = None
    if db_ticket.recurrence_config and db_ticket.recurrence_config.is_active:
        recurrence_type = db_ticket.recurrence_config.recurrence_type

    return Ticket(
        ticket_id=db_ticket.ticket_id,
        title=db_ticket.title,
        description=db_ticket.description,
        status=db_ticket.status,
        priority=db_ticket.priority,
        ticket_type=db_ticket.ticket_type,
        sla=db_ticket.sla,
        created_by=db_ticket.created_by,
        assigned_to=db_ticket.assigned_to,
        created_at=db_ticket.created_at,
        updated_at=db_ticket.updated_at,
        in_progress_at=db_ticket.in_progress_at,
        recurrence_type=recurrence_type,
        creator=TicketEmployee(
            employee_id=db_ticket.creator.employee_id,
            display_name=db_ticket.creator.display_name,
            email=db_ticket.creator.email,
            title=db_ticket.creator.title,
            department=db_ticket.creator.department,
        )
        if db_ticket.creator
        else None,
        assignee=TicketEmployee(
            employee_id=db_ticket.assignee.employee_id,
            display_name=db_ticket.assignee.display_name,
            email=db_ticket.assignee.email,
            title=db_ticket.assignee.title,
            department=db_ticket.assignee.department,
        )
        if db_ticket.assignee
        else None,
    )


# ----------------------------
# 📌 GET /tickets/stats (ANALYTICS AGGREGATED COUNTS)
# ----------------------------
@router.get("/stats")
def get_ticket_stats(
    user_id: str | None = Query(
        None,
        description="Filter by user. 'all' returns all tickets (admin only). "
        "Integer returns tickets for that specific user. "
        "Omitting returns tickets for current user.",
    ),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """
    Return aggregated ticket counts grouped by status, priority, ticket_type, and SLA.
    Admin (AdminActions): sees all tickets. Manager: sees own + subordinates. User: sees only their own.
    """
    scope = get_ticket_visibility_scope(user_permissions, db)
    is_admin = scope["scope"] == "admin"
    allowed_ids = scope["allowed_ids"]

    query = select(Tickets)

    if user_id is not None and user_id.lower() == "all":
        if not is_admin:
            raise HTTPException(status_code=403, detail="Only admins can view all tickets stats")
    elif user_id is not None:
        target_user_id = int(user_id)
        if is_admin:
            query = query.where(
                or_(
                    Tickets.created_by == target_user_id,
                    Tickets.assigned_to == target_user_id,
                )
            )
        else:
            raise HTTPException(status_code=403, detail="Non-admin users can only view their own stats")
    elif not is_admin:
        query = query.where(
            or_(
                Tickets.created_by.in_(allowed_ids),
                Tickets.assigned_to.in_(allowed_ids),
            )
        )

    tickets = db.exec(query).all()

    from collections import defaultdict

    status_counts: dict = defaultdict(int)
    priority_counts: dict = defaultdict(int)
    ticket_type_counts: dict = defaultdict(int)
    sla_counts: dict = defaultdict(int)

    for ticket in tickets:
        status_counts[ticket.status.value] += 1
        priority_counts[ticket.priority.value] += 1
        ticket_type_counts[ticket.ticket_type.value] += 1
        sla_key = ticket.sla.value if ticket.sla else "none"
        sla_counts[sla_key] += 1

    return {
        "status_counts": dict(status_counts),
        "priority_counts": dict(priority_counts),
        "ticket_type_counts": dict(ticket_type_counts),
        "sla_counts": dict(sla_counts),
        "total": len(tickets),
    }


# ----------------------------
# 📌 GET /tickets/stats/users (USERS FOR DROPDOWN)
# ----------------------------
@router.get("/stats/users")
def get_ticket_stats_users(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Return list of employees who have tickets, with their ticket counts. Scoped by visibility tier."""
    scope = get_ticket_visibility_scope(user_permissions, db)
    is_admin = scope["scope"] == "admin"
    allowed_ids = scope["allowed_ids"]

    query = select(Tickets.created_by).distinct()
    created_by_ids = db.exec(query).all()

    query2 = select(Tickets.assigned_to).distinct().where(Tickets.assigned_to.isnot(None))
    assigned_to_ids = db.exec(query2).all()

    all_user_ids = set(created_by_ids + assigned_to_ids)
    if not all_user_ids:
        return []

    # Non-admin: restrict to employees within visibility scope
    if not is_admin:
        all_user_ids &= allowed_ids
        # Manager sees only subordinates (exclude self from dropdown)
        if scope["scope"] == "manager":
            current_id = user_permissions["employee"]["employee_id"]
            all_user_ids.discard(current_id)
        if not all_user_ids:
            return []

    employees = db.exec(select(Employees).where(Employees.employee_id.in_(all_user_ids))).all()

    result = []
    for emp in employees:
        count = db.exec(
            select(Tickets).where(
                or_(
                    Tickets.created_by == emp.employee_id,
                    Tickets.assigned_to == emp.employee_id,
                )
            )
        ).all()
        result.append(
            {
                "employee_id": emp.employee_id,
                "display_name": emp.display_name,
                "email": emp.email,
                "ticket_count": len(count),
            }
        )

    result.sort(key=lambda x: x["display_name"] or "")
    return result


# ----------------------------
# 📌 GET /tickets/assignable-employees (SCOPED EMPLOYEE LIST FOR ASSIGNMENT)
# ----------------------------
@router.get("/assignable-employees", response_model=list[TicketEmployee])
def get_assignable_employees(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Return employees the caller may assign tickets to, scoped by role tier.

    Admin sees all, manager sees self+subordinates, regular user sees IT department only.
    Sorted by display_name.
    """
    allowed_ids = get_assignable_employee_ids(user_permissions, db)
    if not allowed_ids:
        return []

    employees = db.exec(
        select(Employees).where(Employees.employee_id.in_(allowed_ids)).order_by(Employees.display_name)
    ).all()

    return [
        TicketEmployee(
            employee_id=emp.employee_id,
            display_name=emp.display_name,
            email=emp.email,
            title=emp.title,
            department=emp.department,
        )
        for emp in employees
    ]


# ----------------------------
# 📌 GET /tickets (LIST WITH FILTERS AND PAGINATION)
# ----------------------------
@router.get("", response_model=list[Ticket] | PaginatedResponse[Ticket])
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
    limit: int = Query(1000, ge=1, le=1000, description="Maximum number of records to return"),
    with_meta: bool = Query(False, description="Return pagination metadata"),
    db: Session = Depends(get_db),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    """Get tickets with optional filters and pagination. Visibility scoped by role tier."""
    scope = get_ticket_visibility_scope(user_permissions, db)
    is_admin = scope["scope"] == "admin"
    allowed_ids = scope["allowed_ids"]

    # Build base query with relationships
    query = select(Tickets).options(
        selectinload(Tickets.creator),
        selectinload(Tickets.assignee),
        selectinload(Tickets.recurrence_config),
    )

    # Enforce visibility scope (non-admin only)
    filters = []
    if not is_admin:
        filters.append(
            or_(
                Tickets.created_by.in_(allowed_ids),
                Tickets.assigned_to.in_(allowed_ids),
            )
        )

    # Validate out-of-scope params (non-admin only)
    if not is_admin:
        if assigned_to is not None and assigned_to not in allowed_ids:
            raise HTTPException(
                status_code=403,
                detail=f"You do not have permission to view tickets assigned to employee {assigned_to}",
            )
        if created_by is not None and created_by not in allowed_ids:
            raise HTTPException(
                status_code=403,
                detail=f"You do not have permission to view tickets created by employee {created_by}",
            )

    # Apply user-provided filters
    if status:
        filters.append(Tickets.status == status)
    if priority:
        filters.append(Tickets.priority == priority)
    if sla:
        filters.append(sla == Tickets.sla)
    if assigned_to:
        filters.append(Tickets.assigned_to == assigned_to)
    if created_by:
        filters.append(Tickets.created_by == created_by)
    if search:
        search_filter = f"%{search}%"
        filters.append(or_(Tickets.title.ilike(search_filter), Tickets.description.ilike(search_filter)))

    if filters:
        query = query.where(and_(*filters))

    # Apply ordering (newest first) and pagination
    query = query.order_by(Tickets.created_at.desc()).offset(skip).limit(limit)

    tickets = db.exec(query).all()
    items = [ticket_to_schema(ticket) for ticket in tickets]

    if not with_meta:
        return items

    count_query = select(func.count()).select_from(Tickets)
    if filters:
        count_query = count_query.where(and_(*filters))
    total = db.exec(count_query).one()

    return PaginatedResponse[Ticket](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 GET /tickets/{id} (GET SINGLE TICKET)
# ----------------------------
@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get a single ticket by ID."""
    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == ticket_id)
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
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Create a new ticket. Creator is automatically set to the authenticated user."""
    current_employee_id = user_permissions["employee"]["employee_id"]
    logger.info(f"[TICKET_CREATE] Starting ticket creation by employee_id={current_employee_id}")
    logger.info(
        f"[TICKET_CREATE] Ticket details - title={ticket.title}, priority={ticket.priority}, assigned_to={ticket.assigned_to}"
    )

    # Validate assigned employee exists if provided
    if ticket.assigned_to:
        assigned_employee = db.exec(select(Employees).filter(Employees.employee_id == ticket.assigned_to)).first()
        if not assigned_employee:
            logger.error(f"[TICKET_CREATE] Assigned employee not found: employee_id={ticket.assigned_to}")
            raise HTTPException(status_code=404, detail="Assigned employee not found")

        # Scope check: caller must have permission to assign to this employee
        allowed_ids = get_assignable_employee_ids(user_permissions, db)
        if ticket.assigned_to not in allowed_ids:
            logger.error(f"[TICKET_CREATE] Permission denied to assign to employee_id={ticket.assigned_to}")
            raise HTTPException(status_code=403, detail="You do not have permission to assign tickets to this employee")

    # Create ticket
    logger.info("[TICKET_CREATE] Creating database ticket record")
    db_ticket = Tickets(
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        ticket_type=ticket.ticket_type,
        sla=ticket.sla,
        created_by=current_employee_id,
        assigned_to=ticket.assigned_to,
        created_at=utcnow(),
        updated_at=utcnow(),
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    logger.info(f"[TICKET_CREATE] Ticket saved to DB with ticket_id={db_ticket.ticket_id}")

    # Create recurrence config if recurrence_type is set
    if ticket.recurrence_type and ticket.recurrence_type != TicketRecurrenceType.NONE:
        logger.info(
            f"[TICKET_CREATE] Creating recurrence config for ticket_id={db_ticket.ticket_id}, type={ticket.recurrence_type}"
        )
        recurrence_config = TicketRecurrenceConfig(
            ticket_id=db_ticket.ticket_id,
            recurrence_type=ticket.recurrence_type,
            next_occurrence=_calculate_next_occurrence(utcnow(), ticket.recurrence_type),
            parent_ticket_id=None,  # This is the parent/original ticket
            is_active=True,
        )
        db.add(recurrence_config)
        db.commit()
        logger.info(f"[TICKET_CREATE] Recurrence config created for ticket_id={db_ticket.ticket_id}")

    # Load relationships for response
    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == db_ticket.ticket_id)
    ).first()

    # Send notification if ticket has assignee and assignee is different from creator
    if db_ticket.assigned_to and db_ticket.assignee and db_ticket.assigned_to != current_employee_id:
        logger.info(
            f"[TICKET_NOTIFY] Scheduling notification for ticket_id={db_ticket.ticket_id}, assignee_email={db_ticket.assignee.email}"
        )
        background_tasks.add_task(
            notify_ticket_created,
            ticket_id=db_ticket.ticket_id,
            title=db_ticket.title,
            description=db_ticket.description,
            status=db_ticket.status.value,
            priority=db_ticket.priority.value,
            created_by_name=db_ticket.creator.display_name
            or f"{db_ticket.creator.first_name} {db_ticket.creator.last_name}",
            created_by_email=db_ticket.creator.email or "",
            assigned_to_name=db_ticket.assignee.display_name
            or f"{db_ticket.assignee.first_name} {db_ticket.assignee.last_name}",
            assigned_to_email=db_ticket.assignee.email or "",
            action_url=f"{settings.APP_URL}/tickets/{db_ticket.ticket_id}",
            notify_assignee=True,
        )
        logger.info(f"[TICKET_NOTIFY] Notification task added to background queue for ticket_id={db_ticket.ticket_id}")
    else:
        logger.info(
            f"[TICKET_NOTIFY] Skipping notification - assigned_to={db_ticket.assigned_to}, same_as_creator={db_ticket.assigned_to == current_employee_id}"
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
    current_employee_id = user_permissions["employee"]["employee_id"]

    # Get ticket
    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check permissions: creator, assignee, or AdminActions
    is_creator = db_ticket.created_by == current_employee_id
    is_assignee = db_ticket.assigned_to == current_employee_id
    has_admin = has_admin_actions(user_permissions)

    if not (is_creator or is_assignee or has_admin):
        raise HTTPException(
            status_code=403,
            detail="You can only update tickets you created, are assigned to, or have admin permissions",
        )

    # Track if assigned_to changed
    old_assigned_to = db_ticket.assigned_to

    # Validate assigned employee exists if being updated
    if ticket_update.assigned_to is not None and ticket_update.assigned_to:  # If assigning to someone
        assigned_employee = db.exec(
            select(Employees).filter(Employees.employee_id == ticket_update.assigned_to)
        ).first()
        if not assigned_employee:
            raise HTTPException(status_code=404, detail="Assigned employee not found")

        # Scope check: caller must have permission to assign to this employee
        allowed_ids = get_assignable_employee_ids(user_permissions, db)
        if ticket_update.assigned_to not in allowed_ids:
            raise HTTPException(status_code=403, detail="You do not have permission to assign tickets to this employee")

    # Apply updates (exclude recurrence_type - it belongs to TicketRecurrenceConfig, not Tickets)
    update_data = ticket_update.model_dump(exclude_unset=True)
    recurrence_type = update_data.pop("recurrence_type", None)
    for key, value in update_data.items():
        setattr(db_ticket, key, value)

    # Set in_progress_at when ticket moves to in_progress for the first time
    new_status = ticket_update.status
    if new_status == TicketStatus.IN_PROGRESS and db_ticket.in_progress_at is None:
        db_ticket.in_progress_at = utcnow()

    # Handle recurrence: DELETE config if ticket is set to inactive (closed/resolved)
    if new_status == TicketStatus.INACTIVE and db_ticket.recurrence_config:
        db.delete(db_ticket.recurrence_config)

    # Handle recurrence_type update
    if recurrence_type is not None:
        recurrence_type = ticket_update.recurrence_type
        if recurrence_type == TicketRecurrenceType.NONE:
            # Remove recurrence config entirely if user cleared recurrence
            if db_ticket.recurrence_config:
                db.delete(db_ticket.recurrence_config)
        # Create or update recurrence config
        elif db_ticket.recurrence_config:
            db_ticket.recurrence_config.recurrence_type = recurrence_type
            db_ticket.recurrence_config.is_active = True
            db_ticket.recurrence_config.next_occurrence = _calculate_next_occurrence(utcnow(), recurrence_type)
        else:
            recurrence_config = TicketRecurrenceConfig(
                ticket_id=db_ticket.ticket_id,
                recurrence_type=recurrence_type,
                next_occurrence=_calculate_next_occurrence(utcnow(), recurrence_type),
                parent_ticket_id=None,
                is_active=True,
            )
            db.add(recurrence_config)

    # Update timestamp
    db_ticket.updated_at = utcnow()

    db.commit()
    db.refresh(db_ticket)

    # Reload relationships after update
    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

    # Send notification if assigned_to changed and new assignee exists and is different from current user
    if ticket_update.assigned_to is not None and old_assigned_to != db_ticket.assigned_to:  # noqa: SIM102
        if db_ticket.assigned_to and db_ticket.assignee and db_ticket.assigned_to != current_employee_id:
            notification_data = TicketNotificationData(
                ticket_id=db_ticket.ticket_id,
                title=db_ticket.title,
                description=db_ticket.description,
                status=db_ticket.status.value,
                priority=db_ticket.priority.value,
                created_by_name=db_ticket.creator.display_name
                or f"{db_ticket.creator.first_name} {db_ticket.creator.last_name}",
                created_by_email=db_ticket.creator.email or "",
                assigned_to_name=db_ticket.assignee.display_name
                or f"{db_ticket.assignee.first_name} {db_ticket.assignee.last_name}",
                assigned_to_email=db_ticket.assignee.email or "",
                action_url=f"{settings.APP_URL}/tickets/{db_ticket.ticket_id}",
            )
            background_tasks.add_task(
                send_ticket_assigned_notification,
                notification_data=notification_data,
                to_email=db_ticket.assignee.email or "",
            )

    return ticket_to_schema(db_ticket)


# ----------------------------
# 📌 POST /tickets/{id}/stop-recurrence
# ----------------------------
@router.post("/{ticket_id}/stop-recurrence", response_model=Ticket)
async def stop_ticket_recurrence(
    ticket_id: int,
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """Stop the recurrence for a ticket. Only creator, assignee, or AdminActions can stop recurrence."""
    current_employee_id = user_permissions["employee"]["employee_id"]

    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    is_creator = db_ticket.created_by == current_employee_id
    is_assignee = db_ticket.assigned_to == current_employee_id
    has_admin = has_admin_actions(user_permissions)

    if not (is_creator or is_assignee or has_admin):
        raise HTTPException(
            status_code=403,
            detail="You can only stop recurrence on tickets you created, are assigned to, or have admin permissions",
        )

    if db_ticket.recurrence_config and db_ticket.recurrence_config.is_active:
        db.delete(db_ticket.recurrence_config)
        db.commit()

    db_ticket = db.exec(
        select(Tickets)
        .options(
            selectinload(Tickets.creator),
            selectinload(Tickets.assignee),
            selectinload(Tickets.recurrence_config),
        )
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

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
    current_employee_id = user_permissions["employee"]["employee_id"]

    # Get ticket
    db_ticket = db.exec(
        select(Tickets)
        .options(selectinload(Tickets.creator), selectinload(Tickets.assignee))
        .filter(Tickets.ticket_id == ticket_id)
    ).first()

    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check permissions: creator or AdminActions
    is_creator = db_ticket.created_by == current_employee_id
    has_admin = has_admin_actions(user_permissions)

    if not (is_creator or has_admin):
        raise HTTPException(
            status_code=403, detail="Only the ticket creator or users with admin permissions can delete it"
        )

    # Delete recurrence config first (don't let FK SET NULL — delete the config entirely)
    recurrence_config = db.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket_id)
    ).first()
    if recurrence_config:
        db.delete(recurrence_config)

    # Delete the ticket from the database
    db.delete(db_ticket)
    db.commit()
    return {"success": True, "message": "Ticket deleted successfully"}
