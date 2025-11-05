from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from models.tickets import TicketStatus, TicketPriority, TicketSLA
from pydantic import field_validator

# Schema for creating tickets
class TicketCreate(SQLModel):
    Title: str
    Description: Optional[str] = None
    Status: TicketStatus = TicketStatus.TODO
    Priority: TicketPriority = TicketPriority.NORMAL
    SLA: Optional[TicketSLA] = None  # Service Level Agreement
    AssignedTo: Optional[int] = None  # EmployeeId to assign ticket to

# Schema for updating tickets (partial updates allowed)
class TicketUpdate(SQLModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Status: Optional[TicketStatus] = None
    Priority: Optional[TicketPriority] = None
    SLA: Optional[TicketSLA] = None  # Service Level Agreement (can be None to clear)
    AssignedTo: Optional[int] = None  # Can be None to unassign

    @field_validator('SLA', mode='before')
    def validate_sla(cls, v):
        if v == "":
            return None
        return v

# Schema for simplified employee info in ticket responses
class TicketEmployee(SQLModel):
    EmployeeId: int
    DisplayName: Optional[str] = None
    Email: Optional[str] = None
    Title: Optional[str] = None

# Schema for ticket response with related data
class Ticket(SQLModel):
    TicketId: Optional[int] = None
    Title: str
    Description: Optional[str] = None
    Status: TicketStatus
    Priority: TicketPriority
    SLA: Optional[TicketSLA] = None  # Service Level Agreement
    CreatedBy: int
    AssignedTo: Optional[int] = None
    CreatedAt: datetime
    UpdatedAt: datetime

    # Related data
    creator: Optional[TicketEmployee] = None
    assignee: Optional[TicketEmployee] = None

# Schema for ticket filters/pagination
class TicketFilters(SQLModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    sla: Optional[TicketSLA] = None  # Service Level Agreement filter
    assigned_to: Optional[int] = None  # EmployeeId
    created_by: Optional[int] = None   # EmployeeId
    search: Optional[str] = None        # Search in title/description



