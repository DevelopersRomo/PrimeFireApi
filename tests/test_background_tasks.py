"""Regression tests for employee background synchronization."""

from unittest.mock import patch

import pytest
from sqlmodel import select

from core.background_tasks import EmployeeSyncScheduler
from core.microsoft_graph import graph_client as microsoft_graph_client
from models.countries import Countries
from models.employees import Employees


@pytest.mark.asyncio
async def test_process_ms_user_persists_mapped_country_without_sync_errors(db_session) -> None:
    manager = Employees(
        first_name="Sync",
        last_name="Manager",
        display_name="Sync Manager",
        email="manager@primefire.com",
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)

    ms_user = {
        "id": "background-sync-oid",
        "userPrincipalName": "background@primefire.com",
        "mail": "background@primefire.com",
        "displayName": "Background User",
        "givenName": "Background",
        "surname": "User",
        "countryLetterCode": "US",
        "manager": {"displayName": "Sync Manager", "mail": "manager@primefire.com"},
    }
    stats = {
        "total_ms_users": 1,
        "primefire_users": 0,
        "processed": 0,
        "created": 0,
        "updated": 0,
        "errors": 0,
        "countries_created": 0,
    }

    with patch("core.background_tasks.graph_client") as mock_graph:
        mock_graph.map_graph_user_to_employee.side_effect = microsoft_graph_client.map_graph_user_to_employee
        await EmployeeSyncScheduler()._process_ms_user(ms_user, db_session, stats)  # noqa: SLF001

    assert stats == {
        "total_ms_users": 1,
        "primefire_users": 1,
        "processed": 1,
        "created": 1,
        "updated": 0,
        "errors": 0,
        "countries_created": 1,
    }

    country = db_session.exec(select(Countries).where(Countries.name == "US")).one()
    employee = db_session.exec(select(Employees).where(Employees.azure_oid == "background-sync-oid")).one()

    assert employee.country_id == country.country_id
    assert employee.country is country
    assert not isinstance(employee.country, str)
    assert employee.manager_employee_id == manager.employee_id
