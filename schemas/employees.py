from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    Name: Optional[str] = None
    Role: Optional[str] = None        
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Connection: Optional[str] = None  
    Password: Optional[str] = None
    CountryId: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    EmployeeId: int

    class Config:
        orm_mode = True
