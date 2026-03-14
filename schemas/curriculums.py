from sqlmodel import SQLModel

from models.curriculums import Curriculums


# Schema for creating Curriculums (without file)
class CurriculumCreate(SQLModel):
    JobId: int
    Name: str
    Email: str
    Phone: str | None = None
    CoverLetter: str | None = None
    Status: str = "pending"
    EmployeeId: int | None = None


# Schema for updating Curriculums
class CurriculumUpdate(SQLModel):
    Name: str | None = None
    Email: str | None = None
    Phone: str | None = None
    CurriculumPath: str | None = None
    CoverLetter: str | None = None
    Status: str | None = None


# Schema for response (all fields)
class Curriculum(Curriculums):
    pass
