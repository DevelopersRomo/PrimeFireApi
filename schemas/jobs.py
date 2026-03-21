from datetime import datetime

from sqlmodel import SQLModel


class JobCreate(SQLModel):
    title: str
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    status: str = "active"
    employee_id: int | None = None
    country: str | None = None


class JobUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    status: str | None = None
    country: str | None = None


class Job(SQLModel):
    job_id: int | None = None
    title: str
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    status: str
    posted_at: datetime
    employee_id: int | None = None
    country: str | None = None

    class Config:
        from_attributes = True
