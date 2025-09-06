from bd.connection import Base
from sqlalchemy import Column, Integer, String

class Country(Base):
    __tablename__ = "Countries"

    CountryId = Column(Integer, primary_key=True, index=True)
    Name = Column(String, nullable=False)
   