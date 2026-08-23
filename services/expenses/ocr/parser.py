"""Spanish/English receipt heuristics.

This module is pure: it takes recognised text lines and returns an
`ExtractionResult`. No I/O, no OCR engine, no database. That makes it the piece
the fixture corpus regression test exercises directly.

The three ideas that carry the accuracy:

1. Hard exclusions. `CAMBIO`/`CHANGE` and `EFECTIVO`/`CASH` are usually *larger*
   than the total and are the biggest source of naive-extraction errors.
2. Arithmetic self-check. When subtotal + tax + tip - discount matches the total,
   the reading verifies itself and outranks any engine-reported confidence.
3. Layout signals. Lower on the page, further right and taller glyphs all point
   at the total; used as tiebreakers, never on their own.
"""

import re
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation

from services.expenses.ocr.result import Candidate, ExtractionResult, TextLine

# --- Label dictionaries -----------------------------------------------------

# Strong positives: an explicit "amount payable" label.
STRONG_TOTAL_LABELS = (
    "TOTAL A PAGAR",
    "IMPORTE TOTAL",
    "GRAN TOTAL",
    "MONTO TOTAL",
    "SUMA TOTAL",
    "TOTAL GENERAL",
    "TOTAL NETO",
    "AMOUNT DUE",
    "BALANCE DUE",
    "GRAND TOTAL",
    "TOTAL DUE",
    "TOTAL AMOUNT",
    "AMOUNT PAID",
)

# A bare TOTAL. Matched with a boundary so SUBTOTAL never triggers it.
BARE_TOTAL_RE = re.compile(r"(?<![A-Z])TOTAL(?![A-Z])")

SUBTOTAL_LABELS = ("SUBTOTAL", "SUB TOTAL", "SUB-TOTAL", "IMPORTE", "BASE")
TAX_LABELS = ("IVA", "I.V.A", "IEPS", "IMPUESTO", "IMPUESTOS", "TAX", "SALES TAX", "VAT")
TIP_LABELS = ("PROPINA", "TIP", "GRATUITY", "SERVICE CHARGE", "SERVICIO")
DISCOUNT_LABELS = ("DESCUENTO", "DISCOUNT", "DTO", "PROMOCION")

# Never a total. These routinely exceed it and steal a naive extraction.
EXCLUDED_LABELS = (
    "CAMBIO",
    "CHANGE",
    "SU CAMBIO",
    "EFECTIVO",
    "CASH",
    "RECIBIDO",
    "TENDERED",
    "SU PAGO",
    "PAGO CON",
    "ANTICIPO",
    "SALDO ANTERIOR",
    "CREDITO",
    "PUNTOS",
    "AHORRO",
    "TOTAL ARTICULOS",
    "TOTAL ITEMS",
    "TOTAL PIEZAS",
    "NO. DE ARTICULOS",
)

# Lines whose numbers are counts, not money.
COUNT_CONTEXT = ("ARTICULOS", "ITEMS", "PIEZAS", "PZAS", "CANT", "QTY", "UNIDADES", "FOLIO", "CAJA", "TICKET")

# Ordered most specific first: a bare "PESOS" is ambiguous between Mexico and the
# Dominican Republic, so it never decides on its own. Only an unambiguous marker
# does. Puerto Rico uses USD and has no currency of its own.
CURRENCY_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("DOP", ("DOP", "RD$", "RD $", "PESOS DOMINICANOS", "PESO DOMINICANO")),
    ("MXN", ("MXN", "M.N.", "MONEDA NACIONAL", "PESOS MEXICANOS", "PESO MEXICANO")),
    ("USD", ("USD", "US$", "US $", "DLLS", "DOLARES", "DOLLARS", "U.S.D", "USDOLLAR")),
    ("EUR", ("EUR", "€", "EUROS")),
    ("CAD", ("CAD", "C$")),
)

RFC_RE = re.compile(r"\b([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})\b")

MONTHS = {
    "ENE": 1, "ENERO": 1, "JAN": 1, "JANUARY": 1,
    "FEB": 2, "FEBRERO": 2, "FEBRUARY": 2,
    "MAR": 3, "MARZO": 3, "MARCH": 3,
    "ABR": 4, "ABRIL": 4, "APR": 4, "APRIL": 4,
    "MAY": 5, "MAYO": 5,
    "JUN": 6, "JUNIO": 6, "JUNE": 6,
    "JUL": 7, "JULIO": 7, "JULY": 7,
    "AGO": 8, "AGOSTO": 8, "AUG": 8, "AUGUST": 8,
    "SEP": 9, "SEPT": 9, "SEPTIEMBRE": 9, "SEPTEMBER": 9,
    "OCT": 10, "OCTUBRE": 10, "OCTOBER": 10,
    "NOV": 11, "NOVIEMBRE": 11, "NOVEMBER": 11,
    "DIC": 12, "DICIEMBRE": 12, "DEC": 12, "DECEMBER": 12,
}

# A run of digits possibly carrying thousand/decimal separators. The lookbehind
# drops masked card and reference numbers (`*0570`, `#4521`): they sit on the
# payment footer next to a total label and otherwise outrank the real amount.
MONEY_TOKEN_RE = re.compile(r"(?<![*#\d])(?:\d[\d.,\xa0 ]*\d|\d)")

MAX_REASONABLE_AMOUNT = Decimal("10000000")


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_label(value: str) -> str:
    """Uppercase, drop accents, collapse whitespace. Used for label matching."""
    return re.sub(r"\s+", " ", strip_accents(value).upper()).strip()


def normalize_amount(raw: str) -> Decimal | None:
    """Parse a money token written in any of the common ES/EN conventions.

    Handles `1,234.56`, `1.234,56`, `1 234,56`, `1234`, `123.45`.

    The rule: the last separator followed by exactly one or two digits is the
    decimal separator; everything else is a thousands separator. A separator
    followed by three digits is always thousands, never a decimal.
    """
    cleaned = raw.replace(" ", "").replace("\xa0", "").strip()
    # Tolerate a currency symbol or code stuck to the number. Callers include the
    # SAT QR `tt` parameter and hand-typed tokens, not only OCR fragments.
    cleaned = re.sub(r"[^\d.,]", "", cleaned)
    if not cleaned or not any(ch.isdigit() for ch in cleaned):
        return None

    separators = [(index, ch) for index, ch in enumerate(cleaned) if ch in ".,"]

    if not separators:
        digits = cleaned
        decimals = ""
    else:
        last_index, _ = separators[-1]
        tail = cleaned[last_index + 1 :]

        if len(tail) in (1, 2) and tail.isdigit():
            digits = cleaned[:last_index]
            decimals = tail
        else:
            digits = cleaned
            decimals = ""

    digits = re.sub(r"[.,]", "", digits)
    if not digits.isdigit():
        return None

    try:
        value = Decimal(f"{digits}.{decimals}") if decimals else Decimal(digits)
    except InvalidOperation:
        return None

    if value > MAX_REASONABLE_AMOUNT:
        return None
    return value


def money_values(text: str) -> list[Decimal]:
    """Every plausible money amount in a line, left to right."""
    values = []
    for match in MONEY_TOKEN_RE.finditer(text):
        value = normalize_amount(match.group(0))
        if value is not None:
            values.append(value)
    return values


def _has_label(normalized: str, labels: tuple[str, ...]) -> str | None:
    for label in labels:
        if label in normalized:
            return label
    return None


def detect_currency(full_text: str, default: str | None = None) -> str | None:
    """Currency of the document, or `default` when nothing unambiguous appears.

    A bare `$` or a bare `PESOS` never decides: both are shared across the
    countries this serves, and guessing wrong writes a wrong number into an
    expense report that a human then approves.
    """
    normalized = normalize_label(full_text)
    for code, hints in CURRENCY_HINTS:
        for hint in hints:
            if normalize_label(hint) in normalized:
                return code
    return default


def detect_tax_id(full_text: str) -> str | None:
    matches = RFC_RE.findall(strip_accents(full_text).upper())
    return matches[0] if matches else None


def _build_date(day: int, month: int, year: int) -> date | None:
    if year < 100:
        year += 2000
    if not (1 <= month <= 12 and 1 <= day <= 31 and 2000 <= year <= 2100):
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def detect_date(full_text: str) -> date | None:
    """First plausible date in the text, tolerating ES and EN conventions."""
    text = strip_accents(full_text).upper()

    # ISO: 2025-05-23
    iso = re.search(r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b", text)
    if iso:
        built = _build_date(int(iso.group(3)), int(iso.group(2)), int(iso.group(1)))
        if built:
            return built

    # Numeric: 23/05/2025 or 05/23/2025. Mexico writes day first, so that is the
    # default; a first component above 12 confirms it, a second above 12 flips it.
    numeric = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4})\b", text)
    if numeric:
        first, second, year = int(numeric.group(1)), int(numeric.group(2)), int(numeric.group(3))
        day, month = (second, first) if second > 12 >= first else (first, second)
        built = _build_date(day, month, year)
        if built:
            return built

    # Textual month: "23 DE MAYO DE 2025", "23-MAY-2025", "MAY 23, 2025"
    month_names = "|".join(sorted(MONTHS, key=len, reverse=True))
    textual = re.search(rf"\b(\d{{1,2}})\s*(?:DE\s+)?[-\s]?({month_names})\.?\s*(?:DE\s+)?[-\s]?(\d{{2,4}})\b", text)
    if textual:
        built = _build_date(int(textual.group(1)), MONTHS[textual.group(2)], int(textual.group(3)))
        if built:
            return built

    reversed_textual = re.search(rf"\b({month_names})\.?\s+(\d{{1,2}}),?\s+(\d{{4}})\b", text)
    if reversed_textual:
        built = _build_date(
            int(reversed_textual.group(2)),
            MONTHS[reversed_textual.group(1)],
            int(reversed_textual.group(3)),
        )
        if built:
            return built

    return None


def detect_merchant(lines: list[TextLine]) -> str | None:
    """Merchant name is almost always in the first few lines, above the items.

    Skip lines that are mostly digits (tax ids, phones, addresses with numbers)
    and anything shorter than four characters.
    """
    for line in lines[:6]:
        text = line.text.strip()
        if len(text) < 4:
            continue
        digit_ratio = sum(ch.isdigit() for ch in text) / len(text)
        if digit_ratio > 0.3:
            continue
        if RFC_RE.search(strip_accents(text).upper()):
            continue
        return re.sub(r"\s+", " ", text)[:200]
    return None


def _label_context(normalized: str) -> dict[str, bool]:
    return {
        "strong": _has_label(normalized, STRONG_TOTAL_LABELS) is not None,
        "bare_total": BARE_TOTAL_RE.search(normalized) is not None,
        "subtotal": _has_label(normalized, SUBTOTAL_LABELS) is not None,
        "tax": _has_label(normalized, TAX_LABELS) is not None,
        "tip": _has_label(normalized, TIP_LABELS) is not None,
        "discount": _has_label(normalized, DISCOUNT_LABELS) is not None,
        "excluded": _has_label(normalized, EXCLUDED_LABELS) is not None,
        "count": _has_label(normalized, COUNT_CONTEXT) is not None,
    }


def _score_line(line: TextLine, context: dict[str, bool], page_height: int, median_height: float) -> float:
    score = 0.0

    if context["strong"]:
        score += 5.0
    elif context["bare_total"]:
        score += 3.5

    # Position: the total sits low on the ticket.
    if page_height > 0:
        score += 1.5 * min(1.0, line.bottom / page_height)

    # Typography: the total is usually set larger than the item lines.
    if median_height > 0:
        score += min(1.0, max(0.0, (line.box[3] / median_height) - 1.0))

    # Alignment: amounts hug the right edge.
    if page_height > 0 and line.box[0] > 0:
        score += 0.3

    return score


def parse_lines(
    lines: list[TextLine],
    page_height: int = 0,
    page_count: int = 1,
    engine: str = "tesseract",
    base_confidence: float = 0.55,
    currency_default: str | None = None,
) -> ExtractionResult:
    """Turn recognised lines into a structured receipt reading."""
    result = ExtractionResult(engine=engine, page_count=page_count)
    result.raw_text = "\n".join(line.text for line in lines)

    if not lines:
        result.status = "failed"
        result.error_message = "No text recognised in the document"
        return result

    heights = sorted(line.box[3] for line in lines if line.box[3] > 0)
    median_height = heights[len(heights) // 2] if heights else 0.0
    effective_height = page_height or (max(line.bottom for line in lines) if lines else 0)

    candidates: list[Candidate] = []
    subtotal: Decimal | None = None
    tax: Decimal | None = None
    tip: Decimal | None = None
    discount: Decimal | None = None

    for line in lines:
        normalized = normalize_label(line.text)
        values = money_values(line.text)
        if not values:
            continue

        context = _label_context(normalized)

        # The rightmost number on a labelled line is the one that belongs to the
        # label: receipts put the caption on the left and right-align the amount.
        # Taking the largest instead let a rate ("IVA 16% 8.00") or an account
        # number sitting left of the amount win.
        value = values[-1]

        if context["subtotal"] and not context["strong"] and subtotal is None:
            subtotal = value
            continue
        if context["tax"] and tax is None:
            tax = value
            continue
        if context["tip"] and tip is None:
            tip = value
            continue
        if context["discount"] and discount is None:
            discount = value
            continue

        if context["excluded"] or context["count"]:
            continue
        if not (context["strong"] or context["bare_total"]):
            continue
        if value <= 0:
            continue

        candidates.append(
            Candidate(
                value=value,
                label=line.text.strip()[:120],
                score=_score_line(line, context, effective_height, median_height),
                box=line.box,
                page=line.page,
            )
        )

    candidates.sort(key=lambda item: item.score, reverse=True)
    # One entry per distinct amount: a ticket that prints its total again on the
    # payment footer offered the same number twice as an "other amount found".
    seen_values: set[Decimal] = set()
    candidates = [
        candidate
        for candidate in candidates
        if not (candidate.value in seen_values or seen_values.add(candidate.value))
    ]
    result.candidates = candidates[:3]

    result.subtotal = subtotal
    result.tax = tax
    result.tip = tip
    result.currency = detect_currency(result.raw_text, currency_default)
    result.expense_date = detect_date(result.raw_text)
    result.merchant = detect_merchant(lines)
    result.tax_id = detect_tax_id(result.raw_text)

    if not candidates:
        # No labelled total. Fall back to the largest amount in the bottom third,
        # but say so with a low confidence so the UI forces a human check.
        fallback = _fallback_total(lines, effective_height)
        if fallback is None:
            result.status = "failed"
            result.error_message = "No total could be identified"
            return result
        result.total = fallback.value
        result.candidates = [fallback]
        result.confidence = 0.35
        return result

    result.total = candidates[0].value
    result.confidence = base_confidence

    # A total that reconciles with its own parts is worth more than any
    # engine-reported confidence.
    if _arithmetic_matches(result.total, subtotal, tax, tip, discount):
        result.arithmetic_ok = True
        result.confidence = max(result.confidence, 0.95)
    elif candidates[0].score >= 5.0:
        result.confidence = max(result.confidence, 0.8)

    # Two candidates within a hair of each other means the reading is ambiguous.
    if len(candidates) > 1 and abs(candidates[0].score - candidates[1].score) < 0.5:
        if candidates[0].value != candidates[1].value:
            result.confidence = min(result.confidence, 0.6)

    return result


def _fallback_total(lines: list[TextLine], page_height: int) -> Candidate | None:
    """Largest decimal amount in the bottom third, used when no label was found."""
    threshold = page_height * 0.6 if page_height else 0
    best: Candidate | None = None

    for line in lines:
        if threshold and line.bottom < threshold:
            continue
        normalized = normalize_label(line.text)
        if _has_label(normalized, EXCLUDED_LABELS) or _has_label(normalized, COUNT_CONTEXT):
            continue
        for value in money_values(line.text):
            # Require decimals: bare integers down here are usually counts or codes.
            if value <= 0 or value == value.to_integral_value():
                continue
            if best is None or value > best.value:
                best = Candidate(value=value, label=line.text.strip()[:120], score=0.5, box=line.box, page=line.page)

    return best


def _arithmetic_matches(
    total: Decimal | None,
    subtotal: Decimal | None,
    tax: Decimal | None,
    tip: Decimal | None,
    discount: Decimal | None,
) -> bool:
    """True when total reconciles with the parts that were actually found."""
    if total is None or subtotal is None:
        return False

    computed = subtotal + (tax or Decimal(0)) + (tip or Decimal(0)) - (discount or Decimal(0))
    return abs(computed - total) <= Decimal("0.02")


def parse_plain_text(
    text: str,
    engine: str = "pdf_text",
    base_confidence: float = 0.9,
    currency_default: str | None = None,
) -> ExtractionResult:
    """Parse a receipt that arrived as plain text (PDF text layer).

    Line boxes are synthesised from the line order so vertical-position scoring
    still works, even though there is no real layout information.
    """
    raw_lines = [line for line in text.splitlines() if line.strip()]
    lines = [
        TextLine(text=line, box=(0, index * 10, 100, 10), page=1, confidence=100.0)
        for index, line in enumerate(raw_lines)
    ]
    return parse_lines(
        lines,
        page_height=len(raw_lines) * 10,
        engine=engine,
        base_confidence=base_confidence,
        currency_default=currency_default,
    )
