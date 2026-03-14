from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Curriculums(SQLModel, table=True):
    __tablename__ = "Curriculums"
    __table_args__ = {"schema": "dbo"}

    CurriculumId: int | None = Field(default=None, primary_key=True, index=True)
    JobId: int
    Name: str = Field(max_length=100)
    Email: str = Field(max_length=100)
    Phone: str | None = Field(default=None, max_length=20)
    CurriculumPath: str | None = Field(default=None, max_length=255)
    CoverLetter: str | None = Field(default=None, max_length=1000)
    Status: str = Field(default="pending", max_length=20)
    SubmittedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    EmployeeId: int | None = None
