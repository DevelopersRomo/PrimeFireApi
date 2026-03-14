import enum
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


class TicketStatus(enum.StrEnum):
    TODO = "todo"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    DONE = "done"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"


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


class Tickets(SQLModel, table=True):
    __tablename__ = "Tickets"
    __table_args__ = {"schema": "dbo"}

    TicketId: int | None = Field(default=None, primary_key=True, index=True)
    Title: str = Field(max_length=200)
    Description: str | None = Field(default=None, max_length=2000)

    # Status enum
    Status: TicketStatus = Field(default=TicketStatus.TODO, sa_column=Field(sa_type=SAEnum(TicketStatus)))

    # Priority enum
    Priority: TicketPriority = Field(default=TicketPriority.NORMAL, sa_column=Field(sa_type=SAEnum(TicketPriority)))

    # SLA enum (optional)
    SLA: TicketSLA | None = Field(
        default=None, sa_type=SAEnum(TicketSLA, values_callable=lambda x: [e.value for e in x])
    )

    # Foreign keys
    CreatedBy: int = Field(foreign_key="dbo.Employees.EmployeeId")  # Required
    AssignedTo: int | None = Field(default=None, foreign_key="dbo.Employees.EmployeeId")  # Optional

    # Timestamps
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    creator: Optional["Employees"] = Relationship(  # noqa: F821
        back_populates="created_tickets", sa_relationship_kwargs={"foreign_keys": "Tickets.CreatedBy"}
    )
    assignee: Optional["Employees"] = Relationship(  # noqa: F821
        back_populates="assigned_tickets", sa_relationship_kwargs={"foreign_keys": "Tickets.AssignedTo"}
    )
