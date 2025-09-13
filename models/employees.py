from bd.connection import Base
from sqlalchemy import Column, Integer, String, SmallInteger

class Employees(Base):
    __tablename__ = "Employees"

    EmployeeId = Column(Integer, primary_key=True, index=True)
    Name = Column(String(50), nullable=True)
    Role = Column(String(50), nullable=True)   # actualizado
    Email = Column(String(50), nullable=True)
    Phone = Column(String(20), nullable=True)
    Connection = Column(String(50), nullable=True)  # actualizado
    Password = Column(String(20), nullable=True)
    CountryId = Column(SmallInteger, nullable=True)
