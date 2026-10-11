"""Exports must never let user-written text run as a spreadsheet formula."""

import pytest

from core.spreadsheet import neutralize_formula, restore_neutralized


@pytest.mark.parametrize("trigger", ["=", "+", "-", "@", "\t", "\r"])
def test_text_starting_with_a_formula_character_is_prefixed(trigger: str) -> None:
    assert neutralize_formula(f"{trigger}SUM(A1)") == f"'{trigger}SUM(A1)"


@pytest.mark.parametrize("value", ["Panel A", "", "5 - 3", "a=b", "'quoted", None, 12, -3.5, True])
def test_other_values_are_returned_unchanged(value) -> None:
    assert neutralize_formula(value) == value


@pytest.mark.parametrize("value", ["=HYPERLINK(\"http://x\")", "-5 mm", "+1", "@user", "\tx"])
def test_restore_undoes_neutralize(value: str) -> None:
    assert restore_neutralized(neutralize_formula(value)) == value


@pytest.mark.parametrize("value", ["'quoted", "'", "plain", None, 3])
def test_restore_leaves_ordinary_values_alone(value) -> None:
    assert restore_neutralized(value) == value
