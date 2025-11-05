from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import Enum as SAEnum
import enum

class TicketStatus(str, enum.Enum):
    TODO = "todo"
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    DONE = "done"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketSLA(str, enum.Enum):
    HOURS_12 = "12h"
    HOURS_24 = "24h"
    HOURS_48 = "48h"
    WEEKS_1 = "1w"
    WEEKS_2 = "2w"
    WEEKS_4 = "4w"
    
    def __str__(self):
        return self.value

class Tickets(SQLModel, table=True):
    __tablename__ = "Tickets"

    TicketId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Title: str = Field(max_length=200)
    Description: Optional[str] = Field(default=None, max_length=2000)

    # Status enum
    Status: TicketStatus = Field(
        default=TicketStatus.TODO,
        sa_column=Field(sa_type=SAEnum(TicketStatus))
    )

    # Priority enum
    Priority: TicketPriority = Field(
        default=TicketPriority.NORMAL,
        sa_column=Field(sa_type=SAEnum(TicketPriority))
    )

    # SLA enum (optional)
    SLA: Optional[TicketSLA] = Field(
        default=None,
        sa_type=SAEnum(TicketSLA, values_callable=lambda x: [e.value for e in x])
    )

    # Foreign keys
    CreatedBy: int = Field(foreign_key="Employees.EmployeeId")  # Required
    AssignedTo: Optional[int] = Field(default=None, foreign_key="Employees.EmployeeId")  # Optional

    # Timestamps
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    creator: Optional["Employees"] = Relationship(
        back_populates="created_tickets",
        sa_relationship_kwargs={"foreign_keys": "Tickets.CreatedBy"}
    )
    assignee: Optional["Employees"] = Relationship(
        back_populates="assigned_tickets",
        sa_relationship_kwargs={"foreign_keys": "Tickets.AssignedTo"}
    )



