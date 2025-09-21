from sqlmodel import SQLModel
from models.employees import Employees
from typing import Optional

# Schema para crear empleados
class EmployeeCreate(SQLModel):
    Name: Optional[str] = None
    Role: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Connection: Optional[str] = None
    Password: Optional[str] = None
    CountryId: Optional[int] = None

# Schema para respuesta (todos los campos)
class Employee(Employees):
    pass
