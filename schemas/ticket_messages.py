from datetime import datetime

from sqlmodel import SQLModel

from .employees import Employee as EmployeeSchema


class TicketMessageCreate(SQLModel):
    message_txt: str
    ticket_id: int


class TicketMessageUpdate(SQLModel):
    message_txt: str | None = None


class TicketMessage(SQLModel):
    ticket_message_id: int | None = None
    ticket_id: int
    user: EmployeeSchema | None = None
    message_txt: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    edited_at: datetime | None = None


class TicketAttachmentCreate(SQLModel):
    ticket_id: int | None = None
    ticket_message_id: int | None = None
    file_name: str | None = None
    file_type: str | None = None
    file_path: str | None = None


class TicketAttachment(SQLModel):
    ticket_attachment_id: int | None = None
    ticket_id: int
    ticket_message_id: int | None = None
    file_name: str
    file_type: str | None = None
    file_path: str | None = None
    created_at: datetime
