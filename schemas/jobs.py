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

# Schema for updating jobs
class JobUpdate(SQLModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Requirements: Optional[str] = None
    Location: Optional[str] = None
    SalaryMin: Optional[float] = None
    SalaryMax: Optional[float] = None
    Status: Optional[str] = None

# Schema for response (all fields)
class Job(Jobs):
    pass

