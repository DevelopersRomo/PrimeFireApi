"""Contract between the payloads the API sends and the workflows synced to Novu."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import novu_py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from core import ticket_sla_scheduler as sla_job
from core.config import settings
from models.employees import Employees
from models.tickets import TicketSLA, TicketStatus, Tickets
from scripts import sync_novu_workflows
from services.notifications import novu
from services.notifications.novu_workflows import WORKFLOWS
from tests.conftest import create_test_record


def _schema(workflow_id: str) -> dict:
    return next(w for w in WORKFLOWS if w.workflow_id == workflow_id).payload_schema


def test_every_workflow_the_api_triggers_is_defined():
    assert {w.workflow_id for w in WORKFLOWS} == {novu.WORKFLOW_TICKET_CLOSED, novu.WORKFLOW_TICKET_SLA_AT_RISK}


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda w: w.workflow_id)
def test_workflows_are_valid_for_novu_and_convertible_to_updates(workflow):
    assert isinstance(workflow, novu_py.CreateWorkflowDto)
    assert all(isinstance(step.control_values, novu_py.InAppControlDto) for step in workflow.steps)
    # The sync script updates existing workflows with the same content
    assert sync_novu_workflows.to_update(workflow).name == workflow.name


def test_ticket_closed_payload_matches_schema(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    ticket = create_test_record(
        db_session,
        Tickets,
        title="T",
        status=TicketStatus.TODO,
        created_by=other_employee.employee_id,
        assigned_to=current_employee.employee_id,
    )
    db_session.commit()
    with patch("api.tickets.novu.trigger") as trigger:
        response = client.patch(f"/tickets/{ticket.ticket_id}", json={"status": "done"}, headers=auth_headers)
    assert response.status_code == 200

    payload = trigger.call_args.args[3]
    schema = _schema(novu.WORKFLOW_TICKET_CLOSED)
    assert set(payload) == set(schema["properties"])
    assert set(schema["required"]) <= set(payload)


def test_sla_at_risk_payload_matches_schema(db_session: Session, current_employee: Employees, monkeypatch):
    monkeypatch.setattr(settings, "NOVU_SECRET_KEY", "secret")
    now = datetime(2026, 3, 10, 12)  # noqa: DTZ001
    create_test_record(
        db_session,
        Tickets,
        title="T",
        status=TicketStatus.IN_PROGRESS,
        sla=TicketSLA.HOURS_4,
        created_by=current_employee.employee_id,
        sla_running_since=now - timedelta(hours=3),
    )
    db_session.commit()
    with patch("core.ticket_sla_scheduler.novu.trigger") as trigger:
        sla_job.send_sla_warnings(db_session, "main", now)

    payload = trigger.call_args.args[3]
    schema = _schema(novu.WORKFLOW_TICKET_SLA_AT_RISK)
    assert set(payload) == set(schema["properties"])
    assert set(schema["required"]) <= set(payload)


def test_sync_creates_missing_workflows_and_updates_existing_ones():
    client = MagicMock()
    # Novu answers a missing workflow with ErrorDto (seen against the real API), not APIError
    missing = novu_py.models.ErrorDto(MagicMock(), MagicMock(status_code=404, text="Workflow cannot be found"))
    client.workflows.get.side_effect = [missing, MagicMock()]

    result = sync_novu_workflows.sync(client)

    assert client.workflows.create.call_count == 1
    assert client.workflows.update.call_count == 1
    assert result == {WORKFLOWS[0].workflow_id: "created", WORKFLOWS[1].workflow_id: "updated"}


def test_sync_does_not_swallow_other_api_errors():
    client = MagicMock()
    client.workflows.get.side_effect = novu_py.models.ErrorDto(MagicMock(), MagicMock(status_code=401, text="no"))

    with pytest.raises(novu_py.models.NovuError):
        sync_novu_workflows.sync(client)
