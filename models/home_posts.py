from datetime import datetime

from sqlalchemy import Unicode
from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow


class HomePost(SQLModel, table=True):
    """Company news or event shown on the dashboard feed.

    Datetimes are naive UTC. Status (draft/scheduled/published/expired) is derived
    from published_at and expires_at, never stored.
    """

    __tablename__ = "home_posts"
    __table_args__ = {"schema": "dbo"}

    post_id: int | None = Field(default=None, primary_key=True)
    # Unicode types map to NVARCHAR on SQL Server; plain str becomes VARCHAR and turns emoji into "?".
    title: str = Field(max_length=200, sa_type=Unicode(200))
    post_type: str = Field(max_length=10)  # news | event
    body_html: str = Field(sa_type=Unicode)  # sanitized on write; NVARCHAR(MAX)
    event_at: datetime | None = Field(default=None)
    location: str | None = Field(default=None, max_length=200, sa_type=Unicode(200))
    cover_path: str | None = Field(default=None, max_length=500)
    cover_content_type: str | None = Field(default=None, max_length=50)
    is_pinned: bool = Field(default=False)
    published_at: datetime | None = Field(default=None)  # NULL = draft
    expires_at: datetime | None = Field(default=None)
    created_by: int | None = Field(default=None, foreign_key="dbo.employees.employee_id")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    is_active: bool = Field(default=True)
