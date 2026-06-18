"""Azure AD access-token validation (signature, audience, issuer, expiry).

Replaces the previous unverified `jwt.decode(..., verify_signature=False)` usage.
Designed for N tenants: every Azure AD tenant id in `allowed_azure_tenant_ids()`
gets its own cached JWKS client.
"""

import threading
import time
from typing import Any

import jwt  # type: ignore[import-untyped]
from fastapi import HTTPException, status
from jwt import PyJWKClient  # type: ignore[import-untyped]

from core.config import settings

_jwks_clients: dict[str, PyJWKClient] = {}
_jwks_lock = threading.Lock()

# Small in-process cache so the same bearer token is not signature-checked
# twice in a single request (get_db + simple_token_validator).
_payload_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_payload_cache_lock = threading.Lock()
_PAYLOAD_CACHE_MAX = 512


def allowed_azure_tenant_ids() -> set[str]:
    """Azure AD tenant ids accepted by this API. Extend via AZURE_ALLOWED_TENANT_IDS."""
    ids: set[str] = set()
    if settings.TENANT_ID:
        ids.add(settings.TENANT_ID.lower())
    extra = getattr(settings, "AZURE_ALLOWED_TENANT_IDS", "") or ""
    ids.update(t.strip().lower() for t in extra.split(",") if t.strip())
    return ids


def _get_jwks_client(tenant_id: str) -> PyJWKClient:
    with _jwks_lock:
        client = _jwks_clients.get(tenant_id)
        if client is None:
            client = PyJWKClient(
                f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys",
                cache_keys=True,
            )
            _jwks_clients[tenant_id] = client
        return client


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def looks_like_azure_token(token: str) -> bool:
    """Cheap check (no validation) used only to route validation logic."""
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except Exception:
        return False
    return "tid" in payload and ("oid" in payload or "upn" in payload)


def validate_azure_token(token: str) -> dict[str, Any]:
    """Fully validate an Azure AD access token.

    Verifies RS256 signature against the tenant JWKS, audience (this API),
    issuer and expiry. Raises HTTPException 401 on any failure.
    """
    now = time.time()
    with _payload_cache_lock:
        cached = _payload_cache.get(token)
        if cached and cached[0] > now:
            return cached[1]

    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except Exception:
        raise _unauthorized("Invalid token")

    tid = str(unverified.get("tid", "")).lower()
    if not tid or tid not in allowed_azure_tenant_ids():
        raise _unauthorized("Azure AD tenant is not allowed")

    try:
        signing_key = _get_jwks_client(tid).get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=[
                settings.BACKEND_CLIENT_ID,
                f"api://{settings.BACKEND_CLIENT_ID}",
            ],
            leeway=60,
            options={"require": ["exp", "iss"], "verify_iss": False},
        )
    except HTTPException:
        raise
    except Exception:
        raise _unauthorized("Invalid or expired Azure AD token")

    issuer = str(payload.get("iss", ""))
    valid_issuer = (
        issuer.startswith(("https://login.microsoftonline.com/", "https://sts.windows.net/"))
    ) and tid in issuer.lower()
    if not valid_issuer:
        raise _unauthorized("Invalid token issuer")

    exp = float(payload.get("exp", now))
    with _payload_cache_lock:
        if len(_payload_cache) >= _PAYLOAD_CACHE_MAX:
            _payload_cache.clear()
        _payload_cache[token] = (min(exp, now + 300), payload)

    return payload
