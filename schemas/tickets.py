from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel

from models.tickets import TicketPriority, TicketRecurrenceType, TicketSLA, TicketStatus, TicketType


class TicketCreate(SQLModel):
    title: str
    description: str | None = None
    status: TicketStatus = TicketStatus.TODO
    priority: TicketPriority = TicketPriority.NORMAL
    ticket_type: TicketType = TicketType.REQUEST
    sla: TicketSLA | None = None
    assigned_to: int | None = None
    recurrence_type: TicketRecurrenceType | None = None


class TicketUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    ticket_type: TicketType | None = None
    sla: TicketSLA | None = None
    assigned_to: int | None = None
    recurrence_type: TicketRecurrenceType | None = None

    @classmethod
    @field_validator("sla", mode="before")
    def validate_sla(cls, v):
        if not v:
            return None
        return v

    @classmethod
    @field_validator("ticket_type", mode="before")
    def validate_ticket_type(cls, v):
        if not v:
            return None
        return v


class TicketEmployee(SQLModel):
    employee_id: int
    display_name: str | None = None
    email: str | None = None
    title: str | None = None
    department: str | None = None


class Ticket(SQLModel):
    ticket_id: int | None = None
    title: str
    description: str | None = None
    status: TicketStatus
    priority: TicketPriority
    ticket_type: TicketType
    sla: TicketSLA | None = None
    created_by: int
    assigned_to: int | None = None
    created_at: datetime
    updated_at: datetime
    in_progress_at: datetime | None = None
    recurrence_type: TicketRecurrenceType | None = None

    creator: TicketEmployee | None = None
    assignee: TicketEmployee | None = None


class TicketFilters(SQLModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    sla: TicketSLA | None = None
    assigned_to: int | None = None
    created_by: int | None = None
    search: str | None = None
