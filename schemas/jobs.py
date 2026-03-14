from datetime import datetime

from sqlmodel import SQLModel


# Schema for creating jobs
class JobCreate(SQLModel):
    Title: str
    Description: str | None = None
    Requirements: str | None = None
    Location: str | None = None
    SalaryMin: float | None = None
    SalaryMax: float | None = None
    Status: str = "active"
    EmployeeId: int | None = None
    Country: str | None = None  # ISO2 code like "US", "PR", "DO"


# Schema for updating jobs
class JobUpdate(SQLModel):
    Title: str | None = None
    Description: str | None = None
    Requirements: str | None = None
    Location: str | None = None
    SalaryMin: float | None = None
    SalaryMax: float | None = None
    Status: str | None = None
    Country: str | None = None  # ISO2 code like "US", "PR", "DO"


# Schema for response (all fields with Country ISO2 instead of CountryId)
class Job(SQLModel):
    JobId: int | None = None
    Title: str
    Description: str | None = None
    Requirements: str | None = None
    Location: str | None = None
    SalaryMin: float | None = None
    SalaryMax: float | None = None
    Status: str
    PostedAt: datetime
    EmployeeId: int | None = None
    Country: str | None = None  # ISO2 code instead of CountryId

    class Config:
        from_attributes = True
