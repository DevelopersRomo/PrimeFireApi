from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from models.employees import Employees

class Licenses(SQLModel, table=True):
    __tablename__ = "Licenses"
    __table_args__ = {"schema": "dbo"}

    LicenseId: Optional[int] = Field(default=None, primary_key=True)
    Software: Optional[str] = None
    Version: Optional[str] = None
    CreatedAt: Optional[date] = None
    ExpiryDate: Optional[date] = None
    Key: Optional[str] = None
    Account: Optional[str] = None
    Password: Optional[str] = None

    EmployeeId: Optional[int] = Field(
        foreign_key="dbo.Employees.EmployeeId"
    )
    
    Employee: Optional["Employees"] = Relationship(
        back_populates="Licenses"
    )
