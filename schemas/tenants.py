from datetime import datetime

from pydantic import model_validator
from sqlmodel import SQLModel


class TenantCreate(SQLModel):
    name: str
    db_connection_key: str
    description: str | None = None


class TenantUpdate(SQLModel):
    name: str | None = None
    db_connection_key: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TenantRead(SQLModel):
    tenant_id: int
    name: str
    db_connection_key: str
    description: str | None
    is_active: bool
    created_at: datetime


class TenantEmployeeRegister(SQLModel):
    first_name: str
    last_name: str
    phone: str | None = None
    company_name: str
    country: str | None = None


class TenantEmployeeRead(SQLModel):
    id: int
    email: str
    tenant_id: int | None = None
    tenant_name: str | None = None
    created_at: datetime


class ApprovalRequest(SQLModel):
    tenant_employee_id: int
    tenant_id: int


class TenantApprovalRequest(SQLModel):
    tenant_id: int
    status: str = "Active"


class TenantEmployeePendingRead(SQLModel):
    id: int
    email: str
    tenant_id: int | None = None
    tenant_name: str | None = None
    created_at: datetime


class TenantLogoCreate(SQLModel):
    tenant_id: int
    title: str
    description: str | None = None
    path: str
    url: str
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None


class TenantLogoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    path: str | None = None
    url: str | None = None
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None


class TenantLogoRead(SQLModel):
    logo_id: int
    tenant_id: int
    title: str
    description: str | None = None
    path: str
    url: str
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
