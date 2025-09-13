from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LicenceBase(BaseModel):
    Software: str
    Version: str
    ExpiryDate: Optional[datetime] 
    Key: str
    Account: str
    Password: str
    EmployeeID: int

class LicenceCreate(LicenceBase):
    pass

class Licence(LicenceBase):
    LicenceID: int
    CreatedAt: datetime

    class Config:
        orm_mode = True
