from datetime import datetime

from sqlmodel import Field, SQLModel

from core.datetime_utils import utcnow


class Jobs(SQLModel, table=True):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "dbo"}

    job_id: int | None = Field(default=None, primary_key=True, index=True)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    requirements: str | None = Field(default=None, max_length=1000)
    location: str | None = Field(default=None, max_length=100)
    salary_min: float | None = None
    salary_max: float | None = None
    status: str = Field(default="active", max_length=20)
    posted_at: datetime = Field(default_factory=utcnow)
    employee_id: int | None = None
    country_id: int | None = Field(default=None, foreign_key="dbo.countries.country_id")
