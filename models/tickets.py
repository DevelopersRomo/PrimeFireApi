import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from core.datetime_utils import utcnow

if TYPE_CHECKING:
    from models.employees import Employees


class TicketStatus(enum.StrEnum):
    TODO = "todo"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    DONE = "done"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"


# Reaching one of these statuses marks the ticket resolved; leaving them reopens it
RESOLVED_STATUSES = (TicketStatus.DONE, TicketStatus.CLOSED, TicketStatus.INACTIVE)

# SLA time only passes while the ticket is in one of these statuses
SLA_RUNNING_STATUSES = (TicketStatus.ACTIVE, TicketStatus.IN_PROGRESS)


class TicketPriority(enum.StrEnum):
    LOW = "low"
    NORMAL = "normal"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketSLA(enum.StrEnum):
    HOURS_1 = "1h"
    HOURS_4 = "4h"
    HOURS_8 = "8h"
    HOURS_12 = "12h"
    HOURS_24 = "24h"
    HOURS_48 = "48h"
    WEEKS_1 = "1w"
    WEEKS_2 = "2w"
    WEEKS_4 = "4w"
    MONTH_1 = "1m"

    def __str__(self) -> str:
        return self.value


class TicketType(enum.StrEnum):
    ISSUE = "issue"
    REQUEST = "request"
    IMPROVEMENT = "improvement"


class TicketRecurrenceType(enum.StrEnum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    TRIWEEKLY = "triweekly"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    YEARLY = "yearly"


class Tickets(SQLModel, table=True):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "dbo"}

    ticket_id: int | None = Field(default=None, primary_key=True, index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    # Status enum
    status: TicketStatus = Field(
        default=TicketStatus.TODO,
        sa_column=Column(
            SAEnum(TicketStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False
        ),
    )

    # Priority enum
    priority: TicketPriority = Field(
        default=TicketPriority.NORMAL,
        sa_column=Column(
            SAEnum(TicketPriority, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False
        ),
    )

    # SLA enum (optional)
    sla: TicketSLA | None = Field(
        default=None,
        sa_column=Column(
            SAEnum(TicketSLA, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=True
        ),
    )

    # Ticket type enum (required, default issue/request/improvement)
    ticket_type: TicketType = Field(
        default=TicketType.REQUEST,
        sa_column=Column(
            SAEnum(TicketType, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False
        ),
    )

    # Foreign keys
    created_by: int = Field(foreign_key="dbo.employees.employee_id")
    assigned_to: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")

    # Timestamps
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    in_progress_at: datetime | None = Field(default=None)
    resolved_at: datetime | None = Field(default=None)
    sla_warning_sent_at: datetime | None = Field(default=None)
    # SLA clock: seconds accumulated in finished active/in_progress stretches, plus the start of
    # the current stretch (None while the clock is stopped). Elapsed = seconds + (now - since).
    sla_elapsed_seconds: int = Field(default=0)
    sla_running_since: datetime | None = Field(default=None)

    # Relationships
    creator: Optional["Employees"] = Relationship(
        back_populates="created_tickets", sa_relationship_kwargs={"foreign_keys": "Tickets.created_by"}
    )
    assignee: Optional["Employees"] = Relationship(
        back_populates="assigned_tickets", sa_relationship_kwargs={"foreign_keys": "Tickets.assigned_to"}
    )
    recurrence_config: Optional["TicketRecurrenceConfig"] = Relationship(
        back_populates="ticket",
        sa_relationship_kwargs={"foreign_keys": "TicketRecurrenceConfig.ticket_id", "uselist": False},
    )


class TicketRecurrenceConfig(SQLModel, table=True):
    __tablename__ = "ticket_recurrence_config"
    __table_args__ = {"schema": "dbo"}

    config_id: int | None = Field(default=None, primary_key=True, index=True)
    ticket_id: int | None = Field(
        default=None,
        sa_column=Column(ForeignKey("dbo.tickets.ticket_id", ondelete="SET NULL"), nullable=True, index=True),
    )
    recurrence_type: TicketRecurrenceType = Field(default=TicketRecurrenceType.NONE)
    next_occurrence: datetime | None = Field(default=None)
    parent_ticket_id: int | None = Field(default=None)  # no FK: app handles integrity
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)

    ticket: Tickets | None = Relationship(
        back_populates="recurrence_config",
        sa_relationship_kwargs={"foreign_keys": "TicketRecurrenceConfig.ticket_id"},
    )


class TicketEvents(SQLModel, table=True):
    """Audit trail of a ticket: its creation and every tracked field change."""

    __tablename__ = "ticket_events"
    __table_args__ = {"schema": "dbo"}

    event_id: int | None = Field(default=None, primary_key=True, index=True)
    ticket_id: int = Field(foreign_key="dbo.tickets.ticket_id", index=True)
    employee_id: int = Field(foreign_key="dbo.employees.employee_id")
    event_type: str = Field(max_length=20)  # "created" | "changed"
    field: str | None = Field(default=None, max_length=50)
    from_value: str | None = Field(default=None, max_length=100)
    to_value: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=utcnow)

    employee: Optional["Employees"] = Relationship()
