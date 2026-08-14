"""Resolve which named mail profile an outbound notification ships from.

The selector lives on `tenants.mail_profile` and holds a profile key such as
`devromo_tenant` or `primefire_tenant`. The key is what core.mail_profiles turns
into environment variable names, so adding a tenant is a row update plus four
env vars - no code change here.

Callers rarely know their tenant_id, so the common path resolves it through
`tenant_logos.url`, the unique indexed site URL an external integration already
knows about itself.

Resolution order: explicit override > tenant_id > tenant_url > default.
Anything unresolved falls back to the default profile, so a bad or unknown URL
never blocks delivery - it just ships from the address it always shipped from.
"""

import logging

from sqlmodel import Session, select

from core.mail_profiles import DEFAULT_MAIL_PROFILE, normalize_profile_key
from models.tenants import TenantLogos, Tenants

logger = logging.getLogger(__name__)


def _url_candidates(raw: str) -> list[str]:
    """Build the stored-URL spellings worth matching, keeping the unique index usable."""
    cleaned = raw.strip().rstrip("/")
    if not cleaned:
        return []

    bare = cleaned.removeprefix("https://").removeprefix("http://")
    variants = [bare, f"https://{bare}", f"http://{bare}"]
    return list(dict.fromkeys(variants + [f"{variant}/" for variant in variants]))


def resolve_mail_profile(
    db: Session,
    *,
    tenant_url: str | None = None,
    tenant_id: int | None = None,
    override: str | None = None,
) -> str:
    """Resolve the mail profile key for an outbound notification."""
    if override and override.strip():
        return normalize_profile_key(override)

    if tenant_id is None and tenant_url:
        candidates = _url_candidates(tenant_url)
        if candidates:
            logo = db.exec(select(TenantLogos).where(TenantLogos.url.in_(candidates))).first()  # type: ignore[attr-defined]
            if logo:
                tenant_id = logo.tenant_id
            else:
                logger.info("[MAIL_PROFILE] No tenant logo matched url %r, using default", tenant_url)

    if tenant_id is None:
        return DEFAULT_MAIL_PROFILE

    tenant = db.get(Tenants, tenant_id)
    if not tenant:
        logger.info("[MAIL_PROFILE] Tenant %s not found, using default", tenant_id)
        return DEFAULT_MAIL_PROFILE

    return normalize_profile_key(tenant.mail_profile)
