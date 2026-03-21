from sqlmodel import Field, SQLModel


class Countries(SQLModel, table=True):
    __tablename__ = "countries"
    __table_args__ = {"schema": "dbo"}

    country_id: int | None = Field(default=None, primary_key=True, index=True)
    name: str | None = Field(default=None, max_length=100)
