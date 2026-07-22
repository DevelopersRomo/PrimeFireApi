"""Unit tests for the IT quotation calculator."""

from decimal import Decimal

from services.it.quote_calculator import (
    calculate_line,
    calculate_totals,
    validate_payment_percentages,
)


class TestCalculateLine:
    def test_simple_line(self) -> None:
        line = calculate_line(Decimal("1"), Decimal("450"))
        assert line["line_subtotal"] == Decimal("450.00")
        assert line["line_discount"] == Decimal("0.00")
        assert line["line_tax"] == Decimal("0.00")
        assert line["line_total"] == Decimal("450.00")

    def test_quantity_multiplies(self) -> None:
        line = calculate_line(Decimal("3"), Decimal("100"))
        assert line["line_subtotal"] == Decimal("300.00")

    def test_discount_percent(self) -> None:
        line = calculate_line(Decimal("1"), Decimal("200"), discount_percent=Decimal("10"))
        assert line["line_discount"] == Decimal("20.00")
        assert line["line_total"] == Decimal("180.00")

    def test_tax_applies_after_discount(self) -> None:
        line = calculate_line(
            Decimal("1"), Decimal("100"), discount_percent=Decimal("10"), tax_rate=Decimal("16")
        )
        # taxable = 90, tax = 14.40, total = 104.40
        assert line["line_tax"] == Decimal("14.40")
        assert line["line_total"] == Decimal("104.40")

    def test_rounding_half_up(self) -> None:
        line = calculate_line(Decimal("1"), Decimal("0.005"))
        assert line["line_subtotal"] == Decimal("0.01")


class TestCalculateTotals:
    def _item(self, cycle: str, subtotal: str, discount: str = "0", tax: str = "0") -> dict:
        return {
            "billing_cycle": cycle,
            "line_subtotal": Decimal(subtotal),
            "line_discount": Decimal(discount),
            "line_tax": Decimal(tax),
        }

    def test_mockup_quotation_totals(self) -> None:
        """Replica of Q-IT-2026-0012: $600 one-time + $280 annual = $880 initial."""
        items = [
            self._item("ONE_TIME", "450"),
            self._item("ONE_TIME", "150"),
            self._item("ANNUAL", "150"),
            self._item("ANNUAL", "50"),
            self._item("ANNUAL", "80"),
        ]
        totals = calculate_totals(items)
        assert totals["one_time_subtotal"] == Decimal("600.00")
        assert totals["annual_recurring_subtotal"] == Decimal("280.00")
        assert totals["monthly_recurring_subtotal"] == Decimal("0.00")
        assert totals["tax_total"] == Decimal("0.00")
        assert totals["initial_total"] == Decimal("880.00")

    def test_monthly_and_quarterly_normalize_to_monthly(self) -> None:
        items = [
            self._item("MONTHLY", "90"),
            self._item("QUARTERLY", "300"),
        ]
        totals = calculate_totals(items)
        assert totals["monthly_recurring_subtotal"] == Decimal("190.00")
        # Recurring monthly items are not part of the initial amount.
        assert totals["initial_total"] == Decimal("0.00")

    def test_discounts_and_taxes_flow_into_initial(self) -> None:
        items = [self._item("ONE_TIME", "100", discount="10", tax="14.40")]
        totals = calculate_totals(items)
        assert totals["discount_total"] == Decimal("10.00")
        assert totals["tax_total"] == Decimal("14.40")
        assert totals["initial_total"] == Decimal("104.40")

    def test_empty_items(self) -> None:
        totals = calculate_totals([])
        assert totals["initial_total"] == Decimal("0.00")


class TestPaymentPercentages:
    def test_valid_100(self) -> None:
        entries = [{"percentage": 50}, {"percentage": 25}, {"percentage": 25}]
        assert validate_payment_percentages(entries) is True

    def test_invalid_sum(self) -> None:
        entries = [{"percentage": 50}, {"percentage": 25}]
        assert validate_payment_percentages(entries) is False

    def test_amount_only_entries_are_valid(self) -> None:
        entries = [{"percentage": None, "amount": 100}]
        assert validate_payment_percentages(entries) is True

    def test_empty_is_valid(self) -> None:
        assert validate_payment_percentages([]) is True
