from datetime import datetime

from sqlmodel import SQLModel

from .employees import Employee as EmployeeSchema


class TicketMessageCreate(SQLModel):
    MessageTxt: str
    TicketId: int


class TicketMessageUpdate(SQLModel):
    MessageTxt: str | None = None


class TicketMessage(SQLModel):
    TicketMessageId: int | None = None
    TicketId: int
    # Replaced numeric UserId with a nested User object (Employee schema)
    User: EmployeeSchema | None = None
    MessageTxt: str | None = None
    CreatedAt: datetime
    UpdatedAt: datetime | None = None
    EditedAt: datetime | None = None


class TicketAttachmentCreate(SQLModel):
    # TicketId comes from the path param in the endpoint; make optional in body
    TicketId: int | None = None
    TicketMessageId: int | None = None
    FileName: str | None = None
    FileType: str | None = None
    FilePath: str | None = None


class TicketAttachment(SQLModel):
    TicketAttachmentId: int | None = None
    TicketId: int
    TicketMessageId: int | None = None
    FileName: str
    FileType: str | None = None
    FilePath: str | None = None
    CreatedAt: datetime
