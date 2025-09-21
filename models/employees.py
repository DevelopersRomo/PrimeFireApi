from sqlmodel import SQLModel, Field
from typing import Optional

class Employees(SQLModel, table=True):
    __tablename__ = "Employees"

    EmployeeId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Name: Optional[str] = Field(default=None, max_length=50)
    Role: Optional[str] = Field(default=None, max_length=50)
    Email: Optional[str] = Field(default=None, max_length=50)
    Phone: Optional[str] = Field(default=None, max_length=20)
    Connection: Optional[str] = Field(default=None, max_length=50)
    Password: Optional[str] = Field(default=None, max_length=20)
    CountryId: Optional[int] = None
