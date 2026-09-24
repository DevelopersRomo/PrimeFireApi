"""Novu workflows owned by this repo.

Apply them with: python -m scripts.sync_novu_workflows

The payload schemas are the contract with the API (see tests/test_novu_workflows.py): each
key the API sends must be declared here, and Novu rejects triggers that do not match.
Content uses Novu's Liquid syntax ({{ payload.x }}).
"""

from novu_py import (
    ActionDto,
    ChannelPreferenceDto,
    CreateWorkflowDto,
    InAppControlDto,
    InAppStepUpsertDto,
    PreferencesRequestDto,
    PreferencesRequestDtoWorkflow,
    RedirectDto,
    SeverityLevelEnum,
    StepTypeEnum,
    WorkflowPreferenceDto,
)

from services.notifications.novu import WORKFLOW_TICKET_CLOSED, WORKFLOW_TICKET_SLA_AT_RISK

# In-app only: email keeps going through Microsoft Graph. Users may mute these in the Inbox.
_IN_APP_ONLY = PreferencesRequestDto(
    workflow=PreferencesRequestDtoWorkflow(
        all=WorkflowPreferenceDto(enabled=True, read_only=False),
        channels={"in_app": ChannelPreferenceDto(enabled=True)},
    ),
)


def _open_ticket_link() -> RedirectDto:
    return RedirectDto(url="{{ payload.url }}", target="_self")


TICKET_CLOSED = CreateWorkflowDto(
    workflow_id=WORKFLOW_TICKET_CLOSED,
    name="Ticket closed",
    description="Tells the ticket creator and assignee that the ticket was closed (not whoever closed it).",
    tags=["tickets"],
    active=True,
    validate_payload=True,
    payload_schema={
        "type": "object",
        "properties": {
            "ticket_id": {"type": "integer"},
            "title": {"type": "string"},
            "status": {"type": "string", "enum": ["done", "closed", "inactive"]},
            "closed_by": {"type": ["string", "null"]},
            "url": {"type": "string"},
        },
        "required": ["ticket_id", "title", "status", "url"],
        "additionalProperties": False,
    },
    preferences=_IN_APP_ONLY,
    steps=[
        InAppStepUpsertDto(
            name="In-app",
            type=StepTypeEnum.IN_APP,
            step_id="in-app",
            control_values=InAppControlDto(
                subject="Ticket #{{ payload.ticket_id }} closed",
                body='{{ payload.closed_by | default: "Someone" }} set "{{ payload.title }}" to {{ payload.status }}.',
                redirect=_open_ticket_link(),
                primary_action=ActionDto(label="View ticket", redirect=_open_ticket_link()),
            ),
        )
    ],
)

TICKET_SLA_AT_RISK = CreateWorkflowDto(
    workflow_id=WORKFLOW_TICKET_SLA_AT_RISK,
    name="Ticket SLA at risk",
    description="Sent once when a ticket's SLA clock (time in active/in progress) reaches 75%.",
    tags=["tickets", "sla"],
    active=True,
    severity=SeverityLevelEnum.HIGH,
    validate_payload=True,
    payload_schema={
        "type": "object",
        "properties": {
            "ticket_id": {"type": "integer"},
            "title": {"type": "string"},
            "sla": {"type": "string"},
            "deadline": {"type": "string", "format": "date-time"},
            "minutes_left": {"type": "integer"},
            "time_left": {"type": "string"},
            "url": {"type": "string"},
        },
        "required": ["ticket_id", "title", "sla", "deadline", "time_left", "url"],
        "additionalProperties": False,
    },
    preferences=_IN_APP_ONLY,
    steps=[
        InAppStepUpsertDto(
            name="In-app",
            type=StepTypeEnum.IN_APP,
            step_id="in-app",
            control_values=InAppControlDto(
                subject="SLA at risk: ticket #{{ payload.ticket_id }}",
                body='"{{ payload.title }}" has used 75% of its {{ payload.sla }} SLA. Time left: {{ payload.time_left }}.',
                redirect=_open_ticket_link(),
                primary_action=ActionDto(label="Open ticket", redirect=_open_ticket_link()),
            ),
        )
    ],
)

WORKFLOWS = [TICKET_CLOSED, TICKET_SLA_AT_RISK]
