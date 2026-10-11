"""Keep user-written text from running as a formula when an export is opened in a spreadsheet."""

_FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def neutralize_formula(value: object) -> object:
    """Prefix text a spreadsheet would read as a formula with a single quote, so it shows as plain text."""
    if isinstance(value, str) and value.startswith(_FORMULA_TRIGGERS):
        return f"'{value}"
    return value


def restore_neutralized(value: object) -> object:
    """Undo neutralize_formula for files this app exported and the user is importing back."""
    if isinstance(value, str) and value.startswith("'") and value[1:].startswith(_FORMULA_TRIGGERS):
        return value[1:]
    return value
