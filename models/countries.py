from sqlmodel import SQLModel, Field
from typing import Optional

class Countries(SQLModel, table=True):
    __tablename__ = "Countries"

    CountryId: Optional[int] = Field(default=None, primary_key=True, index=True)
    Name: Optional[str] = Field(default=None, max_length=20)
