from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TicketMessages(SQLModel, table=True):
    __tablename__ = "ticketMessages"
    __table_args__ = {"schema": "dbo"}

    TicketMessageId: int | None = Field(default=None, primary_key=True, index=True)
    TicketId: int = Field(foreign_key="dbo.Tickets.TicketId")
    UserId: int = Field(foreign_key="dbo.Employees.EmployeeId")
    MessageTxt: str | None = Field(default=None)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    UpdatedAt: datetime | None = None
    EditedAt: datetime | None = None


class TicketAttachments(SQLModel, table=True):
    __tablename__ = "ticketAttachments"
    __table_args__ = {"schema": "dbo"}

    TicketAttachmentId: int | None = Field(default=None, primary_key=True, index=True)
    TicketId: int = Field(foreign_key="dbo.Tickets.TicketId")
    TicketMessageId: int | None = Field(default=None, foreign_key="dbo.ticketMessages.TicketMessageId")
    FileName: str = Field(max_length=255)
    FileType: str | None = Field(default=None, max_length=100)
    FilePath: str | None = Field(default=None, max_length=500)
    CreatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
