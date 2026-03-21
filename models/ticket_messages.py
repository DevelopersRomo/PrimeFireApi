from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TicketMessages(SQLModel, table=True):
    __tablename__ = "ticket_messages"
    __table_args__ = {"schema": "dbo"}

    ticket_message_id: int | None = Field(default=None, primary_key=True, index=True)
    ticket_id: int = Field(foreign_key="dbo.tickets.ticket_id")
    user_id: int = Field(foreign_key="dbo.employees.employee_id")
    message_txt: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    edited_at: datetime | None = None


class TicketAttachments(SQLModel, table=True):
    __tablename__ = "ticket_attachments"
    __table_args__ = {"schema": "dbo"}

    ticket_attachment_id: int | None = Field(default=None, primary_key=True, index=True)
    ticket_id: int = Field(foreign_key="dbo.tickets.ticket_id")
    ticket_message_id: int | None = Field(default=None, foreign_key="dbo.ticket_messages.ticket_message_id")
    file_name: str = Field(max_length=255)
    file_type: str | None = Field(default=None, max_length=100)
    file_path: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
