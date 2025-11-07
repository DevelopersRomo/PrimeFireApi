from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone


class TicketMessages(SQLModel, table=True):
    __tablename__ = "ticketMessages"
    __table_args__ = {'schema': 'dbo'}

    TicketMessageId: Optional[int] = Field(default=None, primary_key=True, index=True)
    TicketId: int = Field(foreign_key="dbo.Tickets.TicketId")
    UserId: int = Field(foreign_key="dbo.Employees.EmployeeId")
    MessageTxt: Optional[str] = Field(default=None)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    UpdatedAt: Optional[datetime] = None
    EditedAt: Optional[datetime] = None


class TicketAttachments(SQLModel, table=True):
    __tablename__ = "ticketAttachments"
    __table_args__ = {'schema': 'dbo'}

    TicketAttachmentId: Optional[int] = Field(default=None, primary_key=True, index=True)
    TicketId: int = Field(foreign_key="dbo.Tickets.TicketId")
    TicketMessageId: Optional[int] = Field(default=None, foreign_key="dbo.ticketMessages.TicketMessageId")
    FileName: str = Field(max_length=255)
    FileType: Optional[str] = Field(default=None, max_length=100)
    FilePath: Optional[str] = Field(default=None, max_length=500)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
