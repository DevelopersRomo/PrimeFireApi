"""Tests for named mail profiles and outbound tenant resolution."""

import pytest
from sqlmodel import SQLModel, Session, create_engine

import main  # noqa: F401  # configures every SQLModel mapper
from core.mail_profiles import (
    DEFAULT_MAIL_PROFILE,
    env_var_names,
    get_mail_credentials,
    normalize_profile_key,
)
from models.tenants import TenantLogos, Tenants
from schemas.notifications import ContactPrimeFireRequest
from services.notifications import contact_primefire, email_functions
from services.notifications.mail_profile import resolve_mail_profile

DEVROMO = "devromo_tenant"
PRIMEFIRE = "primefire_tenant"


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine, tables=[Tenants.__table__, TenantLogos.__table__])
    with Session(engine) as session:
        session.add(Tenants(tenant_id=1, name="DevRomo", db_connection_key="MAIN", mail_profile=DEVROMO))
        session.add(Tenants(tenant_id=2, name="PrimeFire", db_connection_key="PRIMEFIRE", mail_profile=PRIMEFIRE))
        session.add(
            TenantLogos(
                logo_id=1, tenant_id=1, title="DevRomo", logo_dark="d", logo_light="l", url="https://devromo.com"
            )
        )
        session.add(
            TenantLogos(logo_id=2, tenant_id=2, title="PrimeFire", logo_dark="d", logo_light="l", url="primefire.us")
        )
        session.commit()
        yield session


@pytest.fixture
def devromo_env(monkeypatch):
    monkeypatch.setenv("DEVROMO_TENANT_TENANT_ID", "tenant-guid")
    monkeypatch.setenv("DEVROMO_TENANT_CLIENT_ID", "client-guid")
    monkeypatch.setenv("DEVROMO_TENANT_CLIENT_SECRET", "shhh")
    monkeypatch.setenv("DEVROMO_TENANT_BOT_EMAIL", "noreply@devromo.com")


# --- key naming convention ---


def test_env_var_names_follow_the_key():
    assert env_var_names(DEVROMO) == [
        "DEVROMO_TENANT_TENANT_ID",
        "DEVROMO_TENANT_CLIENT_ID",
        "DEVROMO_TENANT_CLIENT_SECRET",
        "DEVROMO_TENANT_BOT_EMAIL",
    ]


@pytest.mark.parametrize("raw", ["DevRomo_Tenant", "  devromo_tenant  ", "DEVROMO_TENANT"])
def test_keys_are_case_and_whitespace_insensitive(raw):
    assert normalize_profile_key(raw) == DEVROMO


@pytest.mark.parametrize("raw", [None, "", "   ", "bad-key", "has space", "_leading", "sí_acentos"])
def test_unusable_keys_collapse_to_default(raw):
    assert normalize_profile_key(raw) == DEFAULT_MAIL_PROFILE


# --- credential lookup ---


def test_credentials_load_from_the_matching_env_block(devromo_env):
    credentials = get_mail_credentials(DEVROMO)
    assert credentials is not None
    assert credentials.tenant_id == "tenant-guid"
    assert credentials.bot_email == "noreply@devromo.com"


def test_default_profile_has_no_credentials_of_its_own():
    assert get_mail_credentials(DEFAULT_MAIL_PROFILE) is None


def test_unknown_profile_has_no_credentials():
    assert get_mail_credentials("never_configured_tenant") is None


def test_partial_env_block_is_refused_rather_than_half_used(monkeypatch):
    monkeypatch.setenv("HALF_TENANT_TENANT_ID", "t")
    monkeypatch.setenv("HALF_TENANT_CLIENT_ID", "c")
    monkeypatch.delenv("HALF_TENANT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("HALF_TENANT_BOT_EMAIL", raising=False)
    assert get_mail_credentials("half_tenant") is None


def test_adding_a_third_tenant_needs_no_code_change(monkeypatch):
    for field, value in (
        ("TENANT_ID", "t3"),
        ("CLIENT_ID", "c3"),
        ("CLIENT_SECRET", "s3"),
        ("BOT_EMAIL", "hi@acme.com"),
    ):
        monkeypatch.setenv(f"ACME_TENANT_{field}", value)

    credentials = get_mail_credentials("acme_tenant")
    assert credentials is not None
    assert credentials.bot_email == "hi@acme.com"


# --- tenant resolution ---


def test_defaults_when_nothing_identifies_the_tenant(db):
    assert resolve_mail_profile(db) == DEFAULT_MAIL_PROFILE


def test_resolves_the_key_through_the_logo_url(db):
    assert resolve_mail_profile(db, tenant_url="https://devromo.com") == DEVROMO
    assert resolve_mail_profile(db, tenant_url="primefire.us") == PRIMEFIRE


@pytest.mark.parametrize(
    "spelling",
    ["devromo.com", "http://devromo.com", "https://devromo.com/", "  https://devromo.com  "],
)
def test_matches_common_url_spellings(db, spelling):
    assert resolve_mail_profile(db, tenant_url=spelling) == DEVROMO


def test_resolves_by_tenant_id(db):
    assert resolve_mail_profile(db, tenant_id=1) == DEVROMO
    assert resolve_mail_profile(db, tenant_id=2) == PRIMEFIRE


def test_explicit_override_beats_the_database(db):
    assert resolve_mail_profile(db, tenant_url="https://devromo.com", override=PRIMEFIRE) == PRIMEFIRE
    assert resolve_mail_profile(db, tenant_url="primefire.us", override=DEVROMO) == DEVROMO


def test_unknown_url_falls_back_to_default_instead_of_failing(db):
    assert resolve_mail_profile(db, tenant_url="https://nope.example") == DEFAULT_MAIL_PROFILE


def test_unknown_tenant_falls_back_to_default(db):
    assert resolve_mail_profile(db, tenant_id=999) == DEFAULT_MAIL_PROFILE


def test_garbage_override_collapses_to_default(db):
    assert resolve_mail_profile(db, tenant_url="https://devromo.com", override="not a key") == DEFAULT_MAIL_PROFILE


def test_garbage_stored_key_falls_back_to_default(db):
    tenant = db.get(Tenants, 1)
    tenant.mail_profile = "what ever"
    db.add(tenant)
    db.commit()
    assert resolve_mail_profile(db, tenant_id=1) == DEFAULT_MAIL_PROFILE


# --- the contact form sends two emails; both must use the same profile ---


@pytest.mark.asyncio
async def test_both_contact_emails_ship_from_the_resolved_profile(devromo_env, monkeypatch):
    senders = []

    class _Response:
        status_code = 202
        headers = {"x-request-id": "fake"}

        def raise_for_status(self):
            pass

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, url, headers=None, json=None):  # noqa: ARG002
            senders.append(url.split("/users/")[1].split("/sendMail")[0])
            return _Response()

    async def _headers(**kwargs):
        return {"Authorization": "Bearer test"}

    monkeypatch.setattr(email_functions, "get_retry_client", _Client)
    monkeypatch.setattr(email_functions, "get_graph_api_auth_headers", _headers)

    request = ContactPrimeFireRequest(
        name="Ana",
        email="cliente@example.com",
        phone="+18095550000",
        cf_turnstile_response="token",
        to_email="ops@example.com",
    )
    result = await contact_primefire.send_contact_primefire_notification(request, mail_profile=DEVROMO)

    assert result.success
    # First the internal notice, then the confirmation back to the submitter.
    assert senders == ["noreply@devromo.com", "noreply@devromo.com"]
