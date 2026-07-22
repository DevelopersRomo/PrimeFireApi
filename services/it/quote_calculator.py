"""Line and quotation total calculations for IT quotations.

All money math uses Decimal and rounds half-up to 2 decimal places.
Totals rules:
- one_time_subtotal: sum of line subtotals with ONE_TIME billing.
- monthly_recurring_subtotal: sum of MONTHLY line subtotals plus QUARTERLY / 3.
- annual_recurring_subtotal: sum of ANNUAL line subtotals.
- initial_total: amount due on acceptance = one-time + first year of annual
  recurring items, minus discounts, plus taxes (matches the quotation layout
  where Initial Amount = one-time costs + annual recurring for year one).
"""

from decimal import ROUND_HALF_UP, Decimal

TWO_PLACES = Decimal("0.01")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_line(
    quantity: Decimal,
    unit_price: Decimal,
    discount_percent: Decimal = Decimal("0"),
    tax_rate: Decimal = Decimal("0"),
) -> dict[str, Decimal]:
    """Return line_subtotal, line_discount, line_tax and line_total."""
    subtotal = money(Decimal(str(quantity)) * Decimal(str(unit_price)))
    discount = money(subtotal * Decimal(str(discount_percent)) / Decimal("100"))
    taxable = subtotal - discount
    tax = money(taxable * Decimal(str(tax_rate)) / Decimal("100"))
    total = money(taxable + tax)
    return {
        "line_subtotal": subtotal,
        "line_discount": discount,
        "line_tax": tax,
        "line_total": total,
    }


def calculate_totals(items: list[dict]) -> dict[str, Decimal]:
    """Aggregate quotation totals from calculated line dicts.

    Each item dict needs: billing_cycle, line_subtotal, line_discount, line_tax.
    """
    one_time = Decimal("0")
    monthly = Decimal("0")
    annual = Decimal("0")
    discount_total = Decimal("0")
    tax_total = Decimal("0")
    initial_net = Decimal("0")

    for item in items:
        cycle = item["billing_cycle"]
        subtotal = Decimal(str(item["line_subtotal"]))
        discount = Decimal(str(item["line_discount"]))
        tax = Decimal(str(item["line_tax"]))

        discount_total += discount
        tax_total += tax

        if cycle == "ONE_TIME":
            one_time += subtotal
            initial_net += subtotal - discount + tax
        elif cycle == "MONTHLY":
            monthly += subtotal
        elif cycle == "QUARTERLY":
            monthly += subtotal / Decimal("3")
        elif cycle == "ANNUAL":
            annual += subtotal
            # Annual items are due for their first year with the initial payment.
            initial_net += subtotal - discount + tax

    return {
        "one_time_subtotal": money(one_time),
        "monthly_recurring_subtotal": money(monthly),
        "annual_recurring_subtotal": money(annual),
        "discount_total": money(discount_total),
        "tax_total": money(tax_total),
        "initial_total": money(initial_net),
    }


def validate_payment_percentages(entries: list[dict]) -> bool:
    """Percentages, when used, must add up to 100 (0.01 tolerance)."""
    percentages = [Decimal(str(e["percentage"])) for e in entries if e.get("percentage") is not None]
    if not percentages:
        return True
    total = sum(percentages)
    return abs(total - Decimal("100")) <= Decimal("0.01")
