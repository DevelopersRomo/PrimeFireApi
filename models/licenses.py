from sqlmodel import SQLModel, Field
from datetime import date, datetime
from typing import Optional

class Licences(SQLModel, table=True):
    __tablename__ = "Licences"

    LicenceId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Software: Optional[str] = Field(default=None, max_length=50)
    Version: Optional[str] = Field(default=None, max_length=20)
    CreatedAt: Optional[date] = None
    ExpiryDate: Optional[date] = None
    Key: Optional[str] = Field(default=None, max_length=50)
    Account: Optional[str] = Field(default=None, max_length=50)
    Password: Optional[str] = Field(default=None, max_length=50)
    EmployeeId: Optional[int] = None
