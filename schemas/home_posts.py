from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints, field_serializer, field_validator, model_validator

from services.home_posts import sanitize_body_html

PostType = Literal["news", "event"]
PostStatus = Literal["draft", "scheduled", "published", "expired"]


class HomePostWrite(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    post_type: PostType
    body_html: str
    event_at: datetime | None = None
    location: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None
    is_pinned: bool = False
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("body_html")
    @classmethod
    def sanitize_body(cls, value: str) -> str:
        return sanitize_body_html(value)

    @field_validator("event_at", "published_at", "expires_at")
    @classmethod
    def to_naive_utc(cls, value: datetime | None) -> datetime | None:
        # Offset-less input is taken as UTC; storage is naive UTC without microseconds.
        if value is None:
            return None
        if value.tzinfo is not None:
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value.replace(microsecond=0)

    @model_validator(mode="after")
    def check_dates(self) -> "HomePostWrite":
        if self.post_type == "event":
            if self.event_at is None:
                raise ValueError("event_at is required for events")
            self.location = self.location or None
        else:
            self.event_at = None
            self.location = None
        if self.published_at and self.expires_at and self.expires_at <= self.published_at:
            raise ValueError("expires_at must be after published_at")
        return self


class HomePostRead(BaseModel):
    post_id: int
    title: str
    post_type: PostType
    body_html: str
    event_at: datetime | None
    location: str | None
    is_pinned: bool
    published_at: datetime | None
    expires_at: datetime | None
    created_by: int | None
    author_name: str | None
    has_cover: bool
    status: PostStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("event_at", "published_at", "expires_at", "created_at", "updated_at")
    def serialize_utc(self, value: datetime | None) -> str | None:
        # Stored naive UTC; the trailing Z lets clients parse it as UTC.
        return None if value is None else f"{value.replace(tzinfo=None).isoformat()}Z"
