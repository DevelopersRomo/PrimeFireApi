"""Regression tests for the receipt parser.

The parser is pure, so it can be exercised without Tesseract, OpenCV or a
database. These cases lock in the behaviour that actually decides accuracy in
production: the payment-tender traps, the numeric conventions, and the
arithmetic self-check that lifts confidence.

When a real fixture corpus is added under tests/fixtures/receipts/, point an
accuracy test at it and keep these as the fast unit layer.
"""

from datetime import date
from decimal import Decimal

import pytest

from services.expenses.ocr.parser import (
    detect_currency,
    detect_date,
    detect_tax_id,
    normalize_amount,
    parse_plain_text,
)

SPANISH_TICKET = """RESTAURANTE LA PARRILLA SA DE CV
RFC: RPA950612H23
Av. Reforma 123, Villahermosa
FECHA: 20/05/2025  HORA: 14:32
------------------------------
2 ARRACHERA        $ 640.00
1 REFRESCO          $ 45.00
TOTAL ARTICULOS: 3
------------------------------
SUBTOTAL           $ 685.00
IVA 16%            $ 109.60
PROPINA            $ 68.50
TOTAL A PAGAR      $ 863.10
EFECTIVO         $ 1,000.00
CAMBIO             $ 136.90
GRACIAS POR SU COMPRA"""

ENGLISH_RECEIPT = """HILTON GARDEN INN
1234 Main Street, Houston TX
Date: May 23, 2025
Room charge          1,200.00
Parking                 45.00
SUBTOTAL             1,245.00
SALES TAX               99.60
TOTAL DUE            1,344.60
CASH TENDERED        1,400.00
CHANGE                  55.40"""

UNLABELLED_TICKET = """OXXO TIENDA 4521
23/05/2025
COCA COLA 600ML   22.00
SABRITAS          18.50
                  40.50"""

# Real self-checkout ticket. The card footer repeats the total next to a masked
# account number, and "*0570" used to outrank the 62.80 the customer actually paid.
MASKED_ACCOUNT_TICKET = """ S FUNDIDORA (341)
Tiendas Soriana, S.A. de C.V. TSO991022PB6
AV. FRANCISCO I. MADERO 1515
21/08/2026 18:05:01 341 38 38 122
    1 037 CHILE TAJIN GUAJILL   46.90             46.90
    1 229 VINAGRE LA COSTENA    15.90             15.90
                 TOTAL                            62.80
                 TARJETA CREDITO                  62.80
Articulos 2
Cuenta No.: *0570   Total M.N.:$62.80
No. Referencia: 999228"""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1,234.56", "1234.56"),  # US / Mexican convention
        ("1.234,56", "1234.56"),  # European convention
        ("1 234,56", "1234.56"),  # space as thousands separator
        ("1234", "1234"),
        ("123.45", "123.45"),
        ("1.234", "1234"),  # three trailing digits are thousands, never decimals
        ("$ 2,850.00", "2850.00"),  # currency symbol tolerated
        ("MXN 18,200.00", "18200.00"),
    ],
)
def test_normalize_amount_handles_both_conventions(raw, expected):
    assert normalize_amount(raw) == Decimal(expected)


def test_normalize_amount_rejects_non_numeric():
    assert normalize_amount("TOTAL") is None
    assert normalize_amount("") is None


def test_spanish_ticket_ignores_efectivo_and_cambio():
    """The two amounts larger than the total must never win."""
    result = parse_plain_text(SPANISH_TICKET)

    assert result.total == Decimal("863.10")
    assert result.total != Decimal("1000.00")  # EFECTIVO
    assert result.total != Decimal("136.90")  # CAMBIO


def test_spanish_ticket_splits_subtotal_tax_and_tip():
    result = parse_plain_text(SPANISH_TICKET)

    assert result.subtotal == Decimal("685.00")
    assert result.tax == Decimal("109.60")
    assert result.tip == Decimal("68.50")


def test_arithmetic_check_lifts_confidence():
    """685.00 + 109.60 + 68.50 == 863.10, so the reading verifies itself."""
    result = parse_plain_text(SPANISH_TICKET)

    assert result.arithmetic_ok is True
    assert result.confidence >= 0.95


def test_spanish_ticket_reads_date_merchant_and_rfc():
    result = parse_plain_text(SPANISH_TICKET)

    assert result.expense_date == date(2025, 5, 20)
    assert result.merchant == "RESTAURANTE LA PARRILLA SA DE CV"
    assert result.tax_id == "RPA950612H23"


def test_english_receipt_ignores_cash_tendered_and_change():
    result = parse_plain_text(ENGLISH_RECEIPT)

    assert result.total == Decimal("1344.60")
    assert result.subtotal == Decimal("1245.00")
    assert result.tax == Decimal("99.60")
    assert result.arithmetic_ok is True


def test_english_textual_date_is_parsed():
    assert parse_plain_text(ENGLISH_RECEIPT).expense_date == date(2025, 5, 23)


def test_subtotal_never_wins_over_total():
    """SUBTOTAL contains the substring TOTAL and must not be matched as one."""
    result = parse_plain_text(SPANISH_TICKET)

    assert result.total != result.subtotal


def test_unlabelled_ticket_falls_back_with_low_confidence():
    """No label means a guess, and a guess must force a human check."""
    result = parse_plain_text(UNLABELLED_TICKET)

    assert result.total == Decimal("40.50")
    assert result.confidence < 0.5


def test_masked_card_number_is_not_read_as_an_amount():
    result = parse_plain_text(MASKED_ACCOUNT_TICKET)

    assert result.total == Decimal("62.80")
    assert all(candidate.value == Decimal("62.80") for candidate in result.candidates)


def test_labelled_line_takes_the_rightmost_amount_not_the_largest():
    # "Cuenta No.: *0570   Total M.N.:$62.80" carries a total label, so the amount
    # that belongs to it is the one at the right edge, not the biggest on the line.
    result = parse_plain_text("TOTAL M.N. 1500 pts   62.80")

    assert result.total == Decimal("62.80")


def test_repeated_total_is_offered_once():
    result = parse_plain_text(MASKED_ACCOUNT_TICKET)

    assert len(result.candidates) == 1


def test_unambiguous_repeated_total_keeps_its_confidence():
    result = parse_plain_text(MASKED_ACCOUNT_TICKET)

    assert result.confidence >= 0.9


def test_item_count_line_is_not_read_as_money():
    result = parse_plain_text(SPANISH_TICKET)

    assert result.total != Decimal("3")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("TOTAL 100.00 MXN", "MXN"),
        ("Total 100.00 USD", "USD"),
        ("IMPORTE 100.00 M.N.", "MXN"),
        ("TOTAL 100.00 DLLS", "USD"),
        ("TOTAL RD$ 100.00", "DOP"),
        ("TOTAL 100.00 DOP", "DOP"),
        ("TOTAL EN PESOS DOMINICANOS 100.00", "DOP"),
        ("TOTAL EN PESOS MEXICANOS 100.00", "MXN"),
    ],
)
def test_currency_detection(text, expected):
    assert detect_currency(text) == expected


def test_currency_is_not_guessed_from_a_bare_dollar_sign():
    """`$` means a different currency in each country served, so it decides nothing."""
    assert detect_currency("TOTAL $ 100.00") is None


def test_bare_pesos_never_resolves_to_a_country():
    """Mexico and the Dominican Republic both call their money 'pesos'.

    Guessing here would silently file a Dominican receipt as Mexican pesos.
    """
    assert detect_currency("TOTAL 100.00 PESOS") is None


def test_detection_falls_back_to_the_supplied_default():
    assert detect_currency("TOTAL $ 100.00", default="USD") == "USD"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("FECHA 23/05/2025", date(2025, 5, 23)),
        ("FECHA 2025-05-23", date(2025, 5, 23)),
        ("23 DE MAYO DE 2025", date(2025, 5, 23)),
        ("May 23, 2025", date(2025, 5, 23)),
        ("23-MAY-2025", date(2025, 5, 23)),
    ],
)
def test_date_detection_across_formats(text, expected):
    assert detect_date(text) == expected


def test_ambiguous_numeric_date_defaults_to_day_first():
    """Mexico writes the day first; 05/06 is 5 June, not 6 May."""
    assert detect_date("05/06/2025") == date(2025, 6, 5)


def test_numeric_date_flips_when_the_first_part_cannot_be_a_month():
    assert detect_date("23/05/2025") == date(2025, 5, 23)


def test_rfc_detection():
    assert detect_tax_id("RFC: RPA950612H23 EMISOR") == "RPA950612H23"
    assert detect_tax_id("no tax id here") is None


def test_empty_input_fails_cleanly():
    result = parse_plain_text("")

    assert result.status == "failed"
    assert result.total is None
