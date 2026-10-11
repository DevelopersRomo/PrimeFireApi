from datetime import datetime

from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow


class UserSessionVersion(SQLModel, table=True):
    """Revocation counter per account; tokens carry the value they were issued under (claim `tv`)."""

    __tablename__ = "user_session_versions"
    __table_args__ = {"schema": "dbo"}

    email: str = Field(max_length=255, primary_key=True)
    token_version: int = Field(default=0)


class AuthToken(SQLModel, table=True):
    """Tokens para password recovery y magic link."""

    __tablename__ = "auth_tokens"
    __table_args__ = {"schema": "dbo"}

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, index=True)
    token: str = Field(max_length=512, unique=True, index=True)
    token_type: str = Field(max_length=50)  # "password_recovery" | "magic_link"
    expires_at: datetime
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=utcnow)
