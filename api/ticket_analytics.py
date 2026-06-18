from collections import defaultdict
from datetime import datetime, time

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, or_, select

from api.dependencies import get_current_employee_with_permissions
from bd.dependencies import get_db
from models.employees import Employees
from models.tickets import Tickets

router = APIRouter()


def has_admin_actions(user_permissions: dict) -> bool:
    """Check if user has AdminActions permission for tickets module."""
    for perm in user_permissions.get("permissions", []):
        if perm.get("module_key") == "tickets":
            return perm.get("permissions", {}).get("AdminActions", False)
    return False


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
    start_date: datetime | None = Query(
        None,
        description="Filter tickets created on or after this date (inclusive). Format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS",
    ),
    end_date: datetime | None = Query(
        None,
        description="Filter tickets created on or before this date (inclusive). Format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS",
    ),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """
    Return aggregated ticket counts grouped by status, priority, ticket_type, and SLA.

    - Admin (AdminActions): sees all tickets or can filter by specific user_id
    - User (no AdminActions): sees only their own tickets (created_by OR assigned_to)
    """
    current_employee_id = user_permissions["employee"]["employee_id"]
    is_admin = has_admin_actions(user_permissions)

    # Build base query
    query = select(Tickets)

    # Apply user filter
    if user_id is not None and user_id.lower() == "all":
        # Admin explicitly requesting all tickets
        if not is_admin:
            raise PermissionError("Only admins can view all tickets stats")
        # No filter — return all
    elif user_id is not None:
        # Filter by specific user ID
        target_user_id = int(user_id)
        if is_admin:
            # Admin filtering by specific user
            query = query.where(
                or_(
                    Tickets.created_by == target_user_id,
                    Tickets.assigned_to == target_user_id,
                )
            )
        else:
            # Non-admin trying to filter by another user — deny
            raise PermissionError("Non-admin users can only view their own stats")
    # No user_id param — non-admin sees own, admin sees all by default
    elif not is_admin:
        query = query.where(
            or_(
                Tickets.created_by == current_employee_id,
                Tickets.assigned_to == current_employee_id,
            )
        )
        # Admins without user_id param see all (no filter)

    # Apply date range filter
    if start_date:
        query = query.where(Tickets.created_at >= start_date)
    if end_date:
        # Set end_date to end of day if it's a date without time
        end_datetime = end_date
        if end_date.time() == time(0, 0, 0):
            end_datetime = datetime.combine(end_date.date(), time(23, 59, 59))
        query = query.where(Tickets.created_at <= end_datetime)

    tickets = db.exec(query).all()

    # Aggregate
    status_counts: dict[str, int] = defaultdict(int)
    priority_counts: dict[str, int] = defaultdict(int)
    ticket_type_counts: dict[str, int] = defaultdict(int)
    sla_counts: dict[str, int] = defaultdict(int)

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
# 📌 GET /tickets/stats/users (LIST USERS WITH TICKET COUNTS — FOR DROPDOWN)
# ----------------------------
@router.get("/stats/users")
def get_ticket_stats_users(
    user_permissions: dict = Depends(get_current_employee_with_permissions),
    db: Session = Depends(get_db),
):
    """
    Return list of employees who have tickets, with their ticket counts.
    Used for populating the analytics user selector dropdown.
    """
    # Get all distinct user IDs who have tickets (created or assigned)
    query = select(Tickets.created_by).distinct()
    created_by_ids = [row[0] for row in db.exec(query).all()]

    query2 = select(Tickets.assigned_to).distinct().where(Tickets.assigned_to.isnot(None))
    assigned_to_ids = [row[0] for row in db.exec(query2).all()]

    all_user_ids = set(created_by_ids + assigned_to_ids)

    if not all_user_ids:
        return []

    # Fetch employee details for users who have tickets
    employees = db.exec(select(Employees).where(Employees.employee_id.in_(all_user_ids))).all()

    # Build response with count per user
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

    # Sort by display name
    result.sort(key=lambda x: x["display_name"] or "")
    return result
