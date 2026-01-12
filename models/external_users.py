from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ExternalUsers(SQLModel, table=True):
    __tablename__ = "ExternalUsers"
    __table_args__ = {'schema': 'dbo'}

    ExternalUserId: Optional[int] = Field(default=None, primary_key=True)
    Email: str = Field(max_length=100, unique=True)
    PasswordHash: str = Field(max_length=255)
    TenantId: int = Field(foreign_key="dbo.Tenants.TenantId")
    CreatedAt: datetime = Field(default_factory=datetime.now)

    tenant: Optional["Tenants"] = Relationship(back_populates="external_users")

