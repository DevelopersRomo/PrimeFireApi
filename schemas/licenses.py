from sqlmodel import SQLModel
from models.licenses import Licences
from typing import Optional
from datetime import date

# Schema para crear licencias (sin campos autogenerados)
class LicenceCreate(SQLModel):
    Software: str
    Version: str
    ExpiryDate: Optional[date] = None
    Key: str
    Account: str
    Password: str
    EmployeeId: int

# Schema para respuesta (todos los campos)
class Licence(Licences):
    pass
