"""Per-account session version: bumping it invalidates every token issued before the bump."""

from datetime import timedelta

from sqlalchemy import delete, update
from sqlmodel import Session

from core.datetime_utils import utcnow
from models.auth_tokens import RevokedSession, UserSessionVersion

# A revoked session only matters while its refresh token could still be alive (30 days).
REVOKED_SESSION_TTL = timedelta(days=31)


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


def revoke_session(db: Session, sid: str) -> None:
    """Sign out one session only. The caller commits."""
    db.exec(delete(RevokedSession).where(RevokedSession.revoked_at < utcnow() - REVOKED_SESSION_TTL))
    if db.get(RevokedSession, sid) is None:
        db.add(RevokedSession(sid=sid))


def is_session_revoked(db: Session, sid: str | None) -> bool:
    return bool(sid) and db.get(RevokedSession, sid) is not None
