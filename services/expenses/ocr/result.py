"""Shared value objects for the receipt extraction cascade."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class TextLine:
    """One line of recognised text with its bounding box.

    `box` is (x, y, width, height) in pixels. For text-layer PDFs the box is
    still populated so the UI can crop the evidence region.
    """

    text: str
    box: tuple[int, int, int, int] = (0, 0, 0, 0)
    page: int = 1
    confidence: float = 0.0

    @property
    def bottom(self) -> int:
        return self.box[1] + self.box[3]


@dataclass
class Candidate:
    """A possible total, with the evidence that produced it."""

    value: Decimal
    label: str | None = None
    score: float = 0.0
    box: tuple[int, int, int, int] | None = None
    page: int = 1

    def as_dict(self) -> dict:
        return {
            "value": str(self.value),
            "label": self.label,
            "score": round(self.score, 4),
            "box": list(self.box) if self.box else None,
            "page": self.page,
        }


@dataclass
class ExtractionResult:
    """What the cascade hands back to the API layer."""

    engine: str = "tesseract"
    status: str = "done"  # done, failed
    total: Decimal | None = None
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    tip: Decimal | None = None
    currency: str | None = None
    expense_date: date | None = None
    merchant: str | None = None
    tax_id: str | None = None
    uuid: str | None = None
    confidence: float = 0.0
    arithmetic_ok: bool = False
    candidates: list[Candidate] = field(default_factory=list)
    raw_text: str = ""
    page_count: int = 1
    error_message: str | None = None
    duration_ms: int | None = None
