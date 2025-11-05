from sqlmodel import SQLModel
from models.licenses import Licenses
from typing import Optional
from datetime import date

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
    
    

# Schema for response (all fields)
class License(Licenses):
    pass


