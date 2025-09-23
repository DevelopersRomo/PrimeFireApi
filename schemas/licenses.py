from sqlmodel import SQLModel
from models.licenses import Licences
from typing import Optional
from datetime import date

# Schema for creating licenses (without auto-generated fields)
class LicenceCreate(SQLModel):
    Software: str
    Version: str
    ExpiryDate: Optional[date] = None
    Key: str
    Account: str
    Password: str
    EmployeeId: int

# Schema for response (all fields)
class Licence(Licences):
    pass
