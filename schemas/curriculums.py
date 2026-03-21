from datetime import datetime

from sqlmodel import SQLModel


class CurriculumCreate(SQLModel):
    job_id: int
    name: str
    email: str
    phone: str | None = None
    cover_letter: str | None = None
    status: str = "pending"
    employee_id: int | None = None


class CurriculumUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    curriculum_path: str | None = None
    cover_letter: str | None = None
    status: str | None = None


class Curriculum(SQLModel):
    curriculum_id: int | None = None
    job_id: int | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    curriculum_path: str | None = None
    cover_letter: str | None = None
    status: str | None = None
    submitted_at: datetime | None = None
    employee_id: int | None = None

    class Config:
        from_attributes = True
