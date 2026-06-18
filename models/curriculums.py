from datetime import datetime

from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow


class Curriculums(SQLModel, table=True):
    __tablename__ = "curriculums"
    __table_args__ = {"schema": "dbo"}

    curriculum_id: int | None = Field(default=None, primary_key=True, index=True)
    job_id: int
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    curriculum_path: str | None = Field(default=None, max_length=255)
    cover_letter: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=20)
    submitted_at: datetime = Field(default_factory=utcnow)
    employee_id: int | None = None
