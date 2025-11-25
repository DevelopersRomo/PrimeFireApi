from sqlmodel import SQLModel
from models.jobs import Jobs
from typing import Optional
from datetime import datetime

# Schema for creating jobs
class JobCreate(SQLModel):
    Title: str
    Description: Optional[str] = None
    Requirements: Optional[str] = None
    Location: Optional[str] = None
    SalaryMin: Optional[float] = None
    SalaryMax: Optional[float] = None
    Status: str = "active"
    EmployeeId: Optional[int] = None
    Country: Optional[str] = None  # ISO2 code like "US", "PR", "DO"

# Schema for updating jobs
class JobUpdate(SQLModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Requirements: Optional[str] = None
    Location: Optional[str] = None
    SalaryMin: Optional[float] = None
    SalaryMax: Optional[float] = None
    Status: Optional[str] = None
    Country: Optional[str] = None  # ISO2 code like "US", "PR", "DO"

# Schema for response (all fields with Country ISO2 instead of CountryId)
class Job(SQLModel):
    JobId: Optional[int] = None
    Title: str
    Description: Optional[str] = None
    Requirements: Optional[str] = None
    Location: Optional[str] = None
    SalaryMin: Optional[float] = None
    SalaryMax: Optional[float] = None
    Status: str
    PostedAt: datetime
    EmployeeId: Optional[int] = None
    Country: Optional[str] = None  # ISO2 code instead of CountryId
    
    class Config:
        from_attributes = True

