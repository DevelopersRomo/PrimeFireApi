from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Jobs(SQLModel, table=True):
    __tablename__ = "Jobs"
    __table_args__ = {'schema': 'dbo'}

    JobId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Title: str = Field(max_length=100)
    Description: Optional[str] = Field(default=None, max_length=1000)
    Requirements: Optional[str] = Field(default=None, max_length=1000)
    Location: Optional[str] = Field(default=None, max_length=100)
    SalaryMin: Optional[float] = None
    SalaryMax: Optional[float] = None
    Status: str = Field(default="active", max_length=20)
    PostedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    EmployeeId: Optional[int] = None

