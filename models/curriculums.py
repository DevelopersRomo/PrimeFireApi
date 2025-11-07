from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Curriculums(SQLModel, table=True):
    __tablename__ = "Curriculums"
    __table_args__ = {'schema': 'dbo'}

    CurriculumId: Optional[int] = Field(default=None, primary_key=True, index=True)
    JobId: int
    Name: str = Field(max_length=100)
    Email: str = Field(max_length=100)
    Phone: Optional[str] = Field(default=None, max_length=20)
    CurriculumPath: Optional[str] = Field(default=None, max_length=255)
    CoverLetter: Optional[str] = Field(default=None, max_length=1000)
    Status: str = Field(default="pending", max_length=20)
    SubmittedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    EmployeeId: Optional[int] = None

