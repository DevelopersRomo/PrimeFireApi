"""Resolve the tenant_id stamped on IT module rows.

Multitenancy in this project is database-per-tenant (see bd/dependencies.get_db),
but IT tables also carry tenant_id so quotations can be attributed to a tenant.
External users carry tenant_key in their token; internal users map to the
default tenant.
"""

from sqlmodel import Session, select

DEFAULT_TENANT_ID = 1


def resolve_tenant_id(token_data: dict | None, db: Session) -> int:
    tenant_key = (token_data or {}).get("tenant_key")
    if not tenant_key:
        return DEFAULT_TENANT_ID

    from models.tenants import Tenants

    tenant = db.exec(select(Tenants).where(Tenants.db_connection_key == tenant_key)).first()
    if tenant and tenant.tenant_id:
        return tenant.tenant_id
    return DEFAULT_TENANT_ID
