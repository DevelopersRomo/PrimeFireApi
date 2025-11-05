from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
from .employees import Employee as EmployeeSchema


class TicketMessageCreate(SQLModel):
    MessageTxt: str
    TicketId: int


class TicketMessageUpdate(SQLModel):
    MessageTxt: Optional[str] = None


class TicketMessage(SQLModel):
    TicketMessageId: Optional[int] = None
    TicketId: int
    # Replaced numeric UserId with a nested User object (Employee schema)
    User: Optional[EmployeeSchema] = None
    MessageTxt: Optional[str] = None
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    EditedAt: Optional[datetime] = None


class TicketAttachmentCreate(SQLModel):
    # TicketId comes from the path param in the endpoint; make optional in body
    TicketId: Optional[int] = None
    TicketMessageId: Optional[int] = None
    FileName: Optional[str] = None
    FileType: Optional[str] = None
    FilePath: Optional[str] = None


class TicketAttachment(SQLModel):
    TicketAttachmentId: Optional[int] = None
    TicketId: int
    TicketMessageId: Optional[int] = None
    FileName: str
    FileType: Optional[str] = None
    FilePath: Optional[str] = None
    CreatedAt: datetime
