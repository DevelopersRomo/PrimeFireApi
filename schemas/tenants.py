from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel

from core.mail_profiles import is_valid_profile_key

_MAIL_PROFILE_ERROR = (
    "mail_profile must be lowercase letters, digits and underscores, e.g. devromo_tenant"
)


def _clean_mail_profile(value: str | None) -> str | None:
    """Reject keys that cannot become an env var prefix, so typos fail loudly."""
    if value is None:
        return None
    key = value.strip().lower()
    if not is_valid_profile_key(key):
        raise ValueError(_MAIL_PROFILE_ERROR)
    return key


class TenantCreate(SQLModel):
    name: str
    db_connection_key: str
    description: str | None = None
    # Named mail profile key, e.g. devromo_tenant. See core/mail_profiles.py.
    mail_profile: str = "default"

    @field_validator("mail_profile")
    @classmethod
    def validate_mail_profile(cls, value: str) -> str:
        return _clean_mail_profile(value) or "default"


class TenantUpdate(SQLModel):
    name: str | None = None
    db_connection_key: str | None = None
    description: str | None = None
    is_active: bool | None = None
    mail_profile: str | None = None

    @field_validator("mail_profile")
    @classmethod
    def validate_mail_profile(cls, value: str | None) -> str | None:
        return _clean_mail_profile(value)


class TenantRead(SQLModel):
    tenant_id: int
    name: str
    db_connection_key: str
    description: str | None
    is_active: bool
    mail_profile: str = "default"
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
    logo_dark: str
    logo_light: str
    url: str
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None
    auth_provider: str = "password"


class TenantLogoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    logo_dark: str | None = None
    logo_light: str | None = None
    url: str | None = None
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None
    auth_provider: str | None = None


class TenantLogoRead(SQLModel):
    logo_id: int
    tenant_id: int
    title: str
    description: str | None = None
    logo_dark: str
    logo_light: str
    url: str
    email: str | None = None
    path_background: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    tertiary_color: str | None = None
    fav_icon: str | None = None
    auth_provider: str = "password"
    created_at: datetime
    updated_at: datetime | None = None
