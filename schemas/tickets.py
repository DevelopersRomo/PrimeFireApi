from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel

from models.tickets import TicketPriority, TicketSLA, TicketStatus


# Schema for creating tickets
class TicketCreate(SQLModel):
    Title: str
    Description: str | None = None
    Status: TicketStatus = TicketStatus.TODO
    Priority: TicketPriority = TicketPriority.NORMAL
    SLA: TicketSLA | None = None  # Service Level Agreement
    AssignedTo: int | None = None  # EmployeeId to assign ticket to


# Schema for updating tickets (partial updates allowed)
class TicketUpdate(SQLModel):
    Title: str | None = None
    Description: str | None = None
    Status: TicketStatus | None = None
    Priority: TicketPriority | None = None
    SLA: TicketSLA | None = None  # Service Level Agreement (can be None to clear)
    AssignedTo: int | None = None  # Can be None to unassign

    @classmethod
    @field_validator("SLA", mode="before")
    def validate_sla(cls, v):
        if v == "":  # noqa: PLC1901
            return None
        return v


# Schema for simplified employee info in ticket responses
class TicketEmployee(SQLModel):
    EmployeeId: int
    DisplayName: str | None = None
    Email: str | None = None
    Title: str | None = None


# Schema for ticket response with related data
class Ticket(SQLModel):
    TicketId: int | None = None
    Title: str
    Description: str | None = None
    Status: TicketStatus
    Priority: TicketPriority
    SLA: TicketSLA | None = None  # Service Level Agreement
    CreatedBy: int
    AssignedTo: int | None = None
    CreatedAt: datetime
    UpdatedAt: datetime

    # Related data
    creator: TicketEmployee | None = None
    assignee: TicketEmployee | None = None


# Schema for ticket filters/pagination
class TicketFilters(SQLModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    sla: TicketSLA | None = None  # Service Level Agreement filter
    assigned_to: int | None = None  # EmployeeId
    created_by: int | None = None  # EmployeeId
    search: str | None = None  # Search in title/description
