from sqlmodel import SQLModel
from typing import Optional
from datetime import date

from schemas.employees import EmployeeRead

# Schema for creating licenses (without auto-generated fields)
class LicenseCreate(SQLModel):
    Software: str
    Version: str
    CreatedAt: Optional[date] = None
    ExpiryDate: Optional[date] = None
    Key: str
    Account: str
    Password: str
    EmployeeId: int

class LicenseUpdate(SQLModel):
    Software: Optional[str] = None
    Version: Optional[str] = None
    CreatedAt: Optional[date] = None
    ExpiryDate: Optional[date] = None
    Key: Optional[str] = None
    Account: Optional[str] = None
    Password: Optional[str] = None
    EmployeeId: Optional[int] = None
    
class LicenseRead(SQLModel):
    LicenseId: int
    Software: Optional[str]
    Version: Optional[str]
    CreatedAt: Optional[date]
    ExpiryDate: Optional[date]
    Key: Optional[str]
    Account: Optional[str]
    Password: Optional[str]
    EmployeeId: Optional[int]
    Employee: Optional[EmployeeRead] 
class License(LicenseRead):
    pass



