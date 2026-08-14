"""Named mail profiles: map a profile key to one Microsoft tenant's credentials.

A profile key such as `devromo_tenant` reads its credentials from four environment
variables, built by uppercasing the key and appending the field name:

    DEVROMO_TENANT_TENANT_ID
    DEVROMO_TENANT_CLIENT_ID
    DEVROMO_TENANT_CLIENT_SECRET
    DEVROMO_TENANT_BOT_EMAIL

Adding a tenant is therefore config only: define those four variables and point a
row in `tenants.mail_profile` at the key. No code change, no new settings field.

A profile with no complete env block resolves to None and callers fall back to the
legacy MICROSOFT_* credentials plus BOT_EMAIL, so an unconfigured or half-configured
profile keeps delivering mail from the address it always used.
"""

import logging
import os
import re
from dataclasses import dataclass
from functools import lru_cache

from dotenv import dotenv_values

logger = logging.getLogger(__name__)

# Reserved key meaning "the legacy MICROSOFT_* credentials and BOT_EMAIL".
DEFAULT_MAIL_PROFILE = "default"

_CREDENTIAL_FIELDS = ("TENANT_ID", "CLIENT_ID", "CLIENT_SECRET", "BOT_EMAIL")
_PROFILE_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")


@dataclass(frozen=True)
class MailCredentials:
    """One Microsoft tenant's app-only credentials and sender mailbox."""

    tenant_id: str
    client_id: str
    client_secret: str
    bot_email: str


def is_valid_profile_key(raw: str | None) -> bool:
    """True when a key is usable as an environment variable prefix."""
    return bool(raw) and bool(_PROFILE_KEY_PATTERN.match(raw.strip().lower()))


def normalize_profile_key(raw: str | None) -> str:
    """Lowercase and validate a profile key, returning the default when unusable."""
    key = (raw or "").strip().lower()
    if not key:
        return DEFAULT_MAIL_PROFILE
    if not _PROFILE_KEY_PATTERN.match(key):
        logger.warning("[MAIL_PROFILE] Invalid profile key %r, using %s", raw, DEFAULT_MAIL_PROFILE)
        return DEFAULT_MAIL_PROFILE
    return key


@lru_cache(maxsize=1)
def _env_file_values() -> dict[str, str]:
    """Read .env once. Settings loads it too, but never exports it to os.environ."""
    return {key: value for key, value in dotenv_values(".env").items() if value is not None}


def _lookup(name: str) -> str:
    return (os.environ.get(name) or _env_file_values().get(name) or "").strip()


def env_var_names(profile: str) -> list[str]:
    """Return the four env var names a profile reads, for diagnostics and docs."""
    prefix = normalize_profile_key(profile).upper()
    return [f"{prefix}_{field}" for field in _CREDENTIAL_FIELDS]


def get_mail_credentials(profile: str) -> MailCredentials | None:
    """Load a profile's credentials, or None when it is the default or incomplete."""
    key = normalize_profile_key(profile)
    if key == DEFAULT_MAIL_PROFILE:
        return None

    prefix = key.upper()
    values = {field: _lookup(f"{prefix}_{field}") for field in _CREDENTIAL_FIELDS}

    missing = [f"{prefix}_{field}" for field, value in values.items() if not value]
    if missing:
        logger.warning(
            "[MAIL_PROFILE] Profile %r is missing %s - falling back to the default tenant",
            key,
            ", ".join(missing),
        )
        return None

    return MailCredentials(
        tenant_id=values["TENANT_ID"],
        client_id=values["CLIENT_ID"],
        client_secret=values["CLIENT_SECRET"],
        bot_email=values["BOT_EMAIL"],
    )
