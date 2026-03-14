from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Jobs(SQLModel, table=True):
    __tablename__ = "Jobs"
    __table_args__ = {"schema": "dbo"}

    JobId: int | None = Field(default=None, primary_key=True, index=True)
    Title: str = Field(max_length=100)
    Description: str | None = Field(default=None, max_length=1000)
    Requirements: str | None = Field(default=None, max_length=1000)
    Location: str | None = Field(default=None, max_length=100)
    SalaryMin: float | None = None
    SalaryMax: float | None = None
    Status: str = Field(default="active", max_length=20)
    PostedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    EmployeeId: int | None = None
    CountryId: int | None = Field(default=None, foreign_key="dbo.Countries.CountryId")
