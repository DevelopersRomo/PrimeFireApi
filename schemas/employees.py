from sqlmodel import SQLModel
from models.employees import Employees
from typing import Optional

# Schema for creating employees
class EmployeeCreate(SQLModel):
    Name: Optional[str] = None
    Role: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Connection: Optional[str] = None
    Password: Optional[str] = None
    CountryId: Optional[int] = None

# Schema for response (all fields)
class Employee(Employees):
    pass
