from sqlmodel import SQLModel
from models.curriculums import Curriculums
from typing import Optional
from datetime import datetime

# Schema for creating Curriculums (without file)
class CurriculumCreate(SQLModel):
    JobId: int
    Name: str
    Email: str
    Phone: Optional[str] = None
    CoverLetter: Optional[str] = None
    Status: str = "pending"
    EmployeeId: Optional[int] = None

# Schema for updating Curriculums
class CurriculumUpdate(SQLModel):
    Name: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    CurriculumPath: Optional[str] = None
    CoverLetter: Optional[str] = None
    Status: Optional[str] = None

# Schema for response (all fields)
class Curriculum(Curriculums):
    pass

