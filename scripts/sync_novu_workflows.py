"""Create or update the Novu workflows defined in services/notifications/novu_workflows.py.

Usage (from PrimeFireApi/, with NOVU_SECRET_KEY in .env):
    python -m scripts.sync_novu_workflows

Run it once per Novu environment (the Dev and Prod secret keys are different) and again
after editing a workflow definition. Safe to re-run: existing workflows are updated in place.
"""

from novu_py import CreateWorkflowDto, Novu, UpdateWorkflowDto
from novu_py.models import NovuError

from core.config import settings
from services.notifications.novu_workflows import WORKFLOWS


def to_update(workflow: CreateWorkflowDto) -> UpdateWorkflowDto:
    return UpdateWorkflowDto(
        name=workflow.name,
        description=workflow.description,
        tags=workflow.tags,
        active=workflow.active,
        severity=workflow.severity,
        validate_payload=workflow.validate_payload,
        payload_schema=workflow.payload_schema,
        preferences=workflow.preferences,
        steps=workflow.steps,
    )


def sync(client: Novu) -> dict[str, str]:
    result: dict[str, str] = {}
    for workflow in WORKFLOWS:
        try:
            client.workflows.get(workflow_id=workflow.workflow_id)
        except NovuError as error:  # a missing workflow comes back as ErrorDto (404)
            if error.status_code != 404:
                raise
            client.workflows.create(create_workflow_dto=workflow)
            result[workflow.workflow_id] = "created"
            continue
        client.workflows.update(workflow_id=workflow.workflow_id, update_workflow_dto=to_update(workflow))
        result[workflow.workflow_id] = "updated"
    return result


def main() -> None:
    if not settings.NOVU_SECRET_KEY:
        raise SystemExit("NOVU_SECRET_KEY is not set (see .env)")
    with Novu(secret_key=settings.NOVU_SECRET_KEY) as client:
        for workflow_id, action in sync(client).items():
            print(f"{workflow_id}: {action}")  # noqa: T201 - CLI output


if __name__ == "__main__":
    main()
