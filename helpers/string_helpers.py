import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


def parse_email_list(email_string: str) -> list[str]:
    if not email_string:
        return []
    emails = []
    for separator in [";", ","]:
        if separator in email_string:
            emails.extend(email_string.split(separator))
            break
    if not emails:
        emails = [email_string]
    return [e.strip() for e in emails if e.strip() and validate_email(e.strip())]


def format_absence_type(absence_type: str) -> str:
    return absence_type.replace("_", " ").title()


def format_hours_to_readable(decimal_hours: float) -> str:
    hours = int(decimal_hours)
    minutes = round((decimal_hours - hours) * 60)
    if minutes == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{hours} hour{'s' if hours != 1 else ''} {minutes} min"
