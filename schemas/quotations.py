from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from .base import CamelModel


class QuotationCreate(CamelModel):
    CustomerId: int
    QuoteDate: datetime
    ExpirationDate: datetime | None = None
    Subtotal: Decimal = Field(default=Decimal("0.00"))
    Tax: Decimal = Field(default=Decimal("0.00"))
    Discount: Decimal = Field(default=Decimal("0.00"))
    Total: Decimal = Field(default=Decimal("0.00"))
    Status: str
    Notes: str | None = None


class QuotationUpdate(CamelModel):
    CustomerId: int | None = None
    QuoteDate: datetime | None = None
    ExpirationDate: datetime | None = None
    Subtotal: Decimal | None = None
    Tax: Decimal | None = None
    Discount: Decimal | None = None
    Total: Decimal | None = None
    Status: str | None = None
    Notes: str | None = None


class QuotationRead(CamelModel):
    Id: int
    CustomerId: int
    QuoteDate: datetime
    ExpirationDate: datetime | None = None

    Subtotal: Decimal
    Tax: Decimal
    Discount: Decimal
    Total: Decimal

    Status: str
    Notes: str | None = None
    CreatedAt: datetime

    @field_serializer("Subtotal", "Tax", "Discount", "Total")
    def serialize_money(self, v: Decimal):
        return str(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "customerId": 25,
                "quoteDate": "2026-03-05T10:00:00Z",
                "expirationDate": "2026-03-20T10:00:00Z",
                "subtotal": "31350.00",
                "tax": "5016.00",
                "discount": "0.00",
                "total": "36366.00",
                "status": "Draft",
                "notes": "Instalación incluida",
                "createdAt": "2026-03-05T10:00:00Z",
            }
        }
    }


class Quotation(QuotationRead):
    pass
