from bd.connection import Base
from sqlalchemy import Column, Integer, String

class Employee(Base):
    __tablename__ = "Employees"

    EmployeeID = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    Position = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String, nullable=True)
    Connection = Column(String, nullable=True)
    Password = Column(String, nullable=False)
    CountryId = Column(Integer, nullable=False)