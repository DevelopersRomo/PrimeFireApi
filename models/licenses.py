from bd.connection import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class Licences(Base):
    __tablename__ = "Licences"

    LicenceID = Column(Integer, primary_key=True, index=True)
    Software = Column(String, nullable=False)
    Version = Column(String, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    ExpiryDate = Column(DateTime, nullable=False)
    Key = Column(String, unique=True, nullable=False)
    Account = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    EmployeeID = Column(Integer, nullable=False)
