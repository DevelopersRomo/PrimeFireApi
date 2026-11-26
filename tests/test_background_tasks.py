"""Regression tests for employee background synchronization."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlmodel import select

from core.background_tasks import EmployeeSyncScheduler
from core.microsoft_graph import graph_client as microsoft_graph_client
from models.countries import Countries
from models.employees import EmployeeM365Archive, Employees


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


@pytest.mark.asyncio
async def test_complete_sync_archives_absent_id_and_restores_it_when_it_reappears(db_session, monkeypatch):
    missing = Employees(display_name="Absent", azure_oid="missing")
    current = Employees(display_name="Current", azure_oid="current")
    local = Employees(display_name="Local")
    db_session.add_all([missing, current, local])
    db_session.commit()
    employee_id = missing.employee_id

    monkeypatch.setattr("core.background_tasks.engine", db_session.get_bind().engine)
    graph = AsyncMock(side_effect=[[{"id": "current"}], [], [{"id": "current"}, {"id": "missing"}]])
    monkeypatch.setattr("core.background_tasks.graph_client.get_all_users", graph)
    scheduler = EmployeeSyncScheduler()

    await scheduler.sync_employees_from_microsoft()
    assert db_session.exec(select(EmployeeM365Archive.employee_id)).all() == [employee_id]
    assert db_session.get(Employees, employee_id) is not None

    await scheduler.sync_employees_from_microsoft()
    assert db_session.exec(select(EmployeeM365Archive.employee_id)).all() == [employee_id]

    await scheduler.sync_employees_from_microsoft()
    assert db_session.exec(select(EmployeeM365Archive.employee_id)).all() == []
