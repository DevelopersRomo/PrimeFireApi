from sqlmodel import Field, SQLModel


class Countries(SQLModel, table=True):
    __tablename__ = "Countries"
    __table_args__ = {"schema": "dbo"}

    CountryId: int | None = Field(default=None, primary_key=True, index=True)
    Name: str | None = Field(default=None, max_length=20)
