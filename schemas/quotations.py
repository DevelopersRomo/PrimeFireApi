from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_serializer

from .base import SnakeModel


class QuotationCreate(SnakeModel):
    customer_id: int
    quote_date: datetime
    expiration_date: datetime | None = None
    subtotal: Decimal = Field(default=Decimal("0.00"))
    tax: Decimal = Field(default=Decimal("0.00"))
    discount: Decimal = Field(default=Decimal("0.00"))
    total: Decimal = Field(default=Decimal("0.00"))
    status: str
    notes: str | None = None


class QuotationUpdate(SnakeModel):
    customer_id: int | None = None
    quote_date: datetime | None = None
    expiration_date: datetime | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    discount: Decimal | None = None
    total: Decimal | None = None
    status: str | None = None
    notes: str | None = None


class QuotationRead(SnakeModel):
    id: int
    customer_id: int
    quote_date: datetime
    expiration_date: datetime | None = None

    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal

    status: str
    notes: str | None = None
    created_at: datetime

    @field_serializer("subtotal", "tax", "discount", "total")
    def serialize_money(self, v: Decimal):
        return str(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "customer_id": 25,
                "quote_date": "2026-03-05T10:00:00Z",
                "expiration_date": "2026-03-20T10:00:00Z",
                "subtotal": "31350.00",
                "tax": "5016.00",
                "discount": "0.00",
                "total": "36366.00",
                "status": "Draft",
                "notes": "Instalación incluida",
                "created_at": "2026-03-05T10:00:00Z",
            }
        }
    }


class Quotation(QuotationRead):
    pass
