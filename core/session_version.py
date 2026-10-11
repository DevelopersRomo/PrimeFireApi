"""Per-account session version: bumping it invalidates every token issued before the bump."""

from sqlalchemy import update
from sqlmodel import Session

from models.auth_tokens import UserSessionVersion


def _key(email: str) -> str:
    return (email or "").strip().lower()


def current_version(db: Session, email: str) -> int:
    """Version stamped into new tokens; an account that never revoked anything is at 0."""
    row = db.get(UserSessionVersion, _key(email))
    return row.token_version if row else 0


def bump_version(db: Session, email: str) -> None:
    """Invalidate the account's outstanding tokens. The caller commits."""
    key = _key(email)
    bumped = db.exec(
        update(UserSessionVersion)
        .where(UserSessionVersion.email == key)
        .values(token_version=UserSessionVersion.token_version + 1)
    )
    if bumped.rowcount == 0:
        db.add(UserSessionVersion(email=key, token_version=1))
