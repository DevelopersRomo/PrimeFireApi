from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.tickets import get_subordinate_ids, get_ticket_visibility_scope
from models.employees import Employees
from models.tickets import TicketPriority, TicketRecurrenceConfig, TicketRecurrenceType, TicketStatus, Tickets
from tests.conftest import create_test_record

# Fixtures (current_employee, other_employee, auth_overrides) are defined in conftest.py
# They are automatically injected by pytest — no import needed.
current_employee: Employees
other_employee: Employees


def test_create_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, other_employee: Employees, auth_overrides
):
    with patch("api.tickets.notify_ticket_created") as mock_notify:
        payload = {
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "status": "todo",
            "priority": "high",
            "sla": "24h",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Ticket"
        assert data["status"] == "todo"
        assert data["priority"] == "high"
        assert data["sla"] == "24h"
        assert data["created_by"] == current_employee.employee_id
        assert data["assigned_to"] == other_employee.employee_id

        mock_notify.assert_called_once()


def test_get_tickets(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    create_test_record(
        db_session,
        Tickets,
        title="Test Ticket 1",
        description="Desc 1",
        status=TicketStatus.TODO,
        priority=TicketPriority.LOW,
        created_by=current_employee.employee_id,
    )
    create_test_record(
        db_session,
        Tickets,
        title="Test Ticket 2",
        description="Desc 2",
        status=TicketStatus.DONE,
        priority=TicketPriority.HIGH,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    response = client.get("/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # test filtering
    response = client.get("/tickets?status=done", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(t["status"] == "done" for t in data)


def test_get_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    db_session.commit()

    response = client.get(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Ticket"


def test_update_ticket(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    with patch("api.tickets.send_ticket_assigned_notification") as mock_notify:
        ticket = create_test_record(
            db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
        )
        db_session.commit()

        payload = {"status": "in_progress", "assigned_to": other_employee.employee_id}

        response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == other_employee.employee_id

        mock_notify.assert_called_once()


def test_delete_ticket(
    client: TestClient, auth_headers: dict, current_employee: Employees, db_session: Session, auth_overrides
):
    ticket = create_test_record(
        db_session, Tickets, title="Test Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    db_session.commit()

    response = client.delete(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/tickets/{ticket.ticket_id}", headers=auth_headers)
    assert response.status_code == 404


# =============================================================================
# Recurrence Tests
# =============================================================================


def test_create_ticket_with_recurrence(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Creating a ticket with recurrence_type should create a TicketRecurrenceConfig."""
    with patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Recurring Ticket",
            "description": "Test recurring ticket",
            "status": "todo",
            "priority": "high",
            "recurrence_type": "weekly",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_type"] == "weekly"

        # Verify config was created in DB
        config = db_session.exec(
            select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == data["ticket_id"])
        ).first()
        assert config is not None
        assert config.recurrence_type == TicketRecurrenceType.WEEKLY
        assert config.is_active is True
        assert config.next_occurrence is not None


def test_create_ticket_without_recurrence(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Creating a ticket without recurrence_type should NOT create a TicketRecurrenceConfig."""
    with patch("api.tickets.notify_ticket_created"):
        payload = {
            "title": "Normal Ticket",
            "description": "No recurrence",
            "status": "todo",
            "priority": "low",
            "assigned_to": other_employee.employee_id,
        }

        response = client.post("/tickets", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["recurrence_type"] is None

        # Verify no config was created
        config = db_session.exec(
            select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == data["ticket_id"])
        ).first()
        assert config is None


def test_update_ticket_recurrence_type(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Updating recurrence_type on an existing ticket should create/update the config."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # Update with recurrence
    payload = {"recurrence_type": "monthly"}
    response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] == "monthly"

    db_session.expire_all()  # Force re-fetch so we see DB state, not identity-map cache
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None
    assert config.recurrence_type == TicketRecurrenceType.MONTHLY

    # Update recurrence type
    payload = {"recurrence_type": "biweekly"}
    response = client.patch(f"/tickets/{ticket.ticket_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] == "biweekly"

    db_session.expire_all()  # Force re-fetch after second update
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None
    assert config.recurrence_type == TicketRecurrenceType.BIWEEKLY


def test_update_recurrence_type_to_none_deletes_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Setting recurrence_type to 'none' should DELETE the TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "weekly"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Now clear recurrence
    response = client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "none"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["recurrence_type"] is None

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None  # Deleted, not just inactive


def test_update_status_to_inactive_deletes_recurrence_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Setting status to 'inactive' should DELETE the TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "daily"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Now set to inactive
    response = client.patch(
        f"/tickets/{ticket.ticket_id}", json={"status": "inactive", "recurrence_type": "none"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None  # Deleted


def test_delete_ticket_deletes_recurrence_config(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Deleting a ticket should also DELETE its TicketRecurrenceConfig."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()
    ticket_id = ticket.ticket_id

    # First add recurrence
    client.patch(f"/tickets/{ticket_id}", json={"recurrence_type": "yearly"}, headers=auth_headers)

    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket_id)
    ).first()
    assert config is not None

    # Delete the ticket
    response = client.delete(f"/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200

    # Config should be gone too
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket_id)
    ).first()
    assert config is None


def test_stop_recurrence_endpoint(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """POST /tickets/{id}/stop-recurrence should delete the recurrence config."""
    ticket = create_test_record(
        db_session,
        Tickets,
        title="Test Ticket",
        status=TicketStatus.TODO,
        created_by=current_employee.employee_id,
    )
    db_session.commit()

    # First add recurrence
    client.patch(f"/tickets/{ticket.ticket_id}", json={"recurrence_type": "weekly"}, headers=auth_headers)

    db_session.expire_all()
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is not None

    # Stop recurrence
    response = client.post(f"/tickets/{ticket.ticket_id}/stop-recurrence", headers=auth_headers)
    assert response.status_code == 200

    db_session.expire_all()  # Force re-fetch after deletion
    config = db_session.exec(
        select(TicketRecurrenceConfig).filter(TicketRecurrenceConfig.ticket_id == ticket.ticket_id)
    ).first()
    assert config is None


# =============================================================================
# Unit: get_subordinate_ids (Task 1.1)
# =============================================================================


def test_get_subordinate_ids_returns_empty_when_no_subordinates(db_session: Session):
    """Manager with no subordinates returns empty list."""
    manager = create_test_record(
        db_session,
        Employees,
        email="manager_empty@example.com",
        first_name="No",
        last_name="Subs",
        display_name="No Subordinates",
    )
    db_session.commit()

    result = get_subordinate_ids(manager.employee_id, db_session)
    assert result == []


def test_get_subordinate_ids_returns_direct_subordinates(db_session: Session):
    """Manager with direct reports returns their IDs."""
    manager = create_test_record(
        db_session,
        Employees,
        email="manager_dir@example.com",
        first_name="Has",
        last_name="Directs",
        display_name="Has Directs",
    )
    sub1 = create_test_record(
        db_session,
        Employees,
        email="sub_dir1@example.com",
        first_name="Direct",
        last_name="One",
        display_name="Direct One",
        manager_employee_id=manager.employee_id,
    )
    sub2 = create_test_record(
        db_session,
        Employees,
        email="sub_dir2@example.com",
        first_name="Direct",
        last_name="Two",
        display_name="Direct Two",
        manager_employee_id=manager.employee_id,
    )
    db_session.commit()

    result = get_subordinate_ids(manager.employee_id, db_session)
    assert sorted(result) == sorted([sub1.employee_id, sub2.employee_id])


def test_get_subordinate_ids_returns_nested_subordinates(db_session: Session):
    """Manager with 2-level hierarchy returns all subordinates."""
    manager = create_test_record(
        db_session,
        Employees,
        email="top_mgr@example.com",
        first_name="Top",
        last_name="Manager",
        display_name="Top Manager",
    )
    mid = create_test_record(
        db_session,
        Employees,
        email="mid_mgr@example.com",
        first_name="Mid",
        last_name="Manager",
        display_name="Mid Manager",
        manager_employee_id=manager.employee_id,
    )
    leaf = create_test_record(
        db_session,
        Employees,
        email="leaf_emp@example.com",
        first_name="Leaf",
        last_name="Employee",
        display_name="Leaf Employee",
        manager_employee_id=mid.employee_id,
    )
    db_session.commit()

    result = get_subordinate_ids(manager.employee_id, db_session)
    assert sorted(result) == sorted([mid.employee_id, leaf.employee_id])


def test_get_subordinate_ids_excludes_self(db_session: Session):
    """Manager's own ID is NOT in the result."""
    manager = create_test_record(
        db_session,
        Employees,
        email="self_mgr@example.com",
        first_name="Self",
        last_name="Manager",
        display_name="Self Manager",
    )
    sub = create_test_record(
        db_session,
        Employees,
        email="self_sub@example.com",
        first_name="Self",
        last_name="Sub",
        display_name="Self Sub",
        manager_employee_id=manager.employee_id,
    )
    db_session.commit()

    result = get_subordinate_ids(manager.employee_id, db_session)
    assert manager.employee_id not in result
    assert sub.employee_id in result


# =============================================================================
# Unit: get_ticket_visibility_scope (Task 1.2)
# =============================================================================


def test_get_ticket_visibility_scope_admin(db_session: Session):
    """Employee with admin_actions on tickets returns admin scope."""
    emp = create_test_record(
        db_session,
        Employees,
        email="admin_vis@example.com",
        first_name="Admin",
        last_name="User",
        display_name="Admin User",
    )
    db_session.commit()

    user_permissions = {
        "employee": {"employee_id": emp.employee_id, "email": emp.email},
        "permissions": [
            {"module_key": "tickets", "permissions": {"admin_actions": True}},
        ],
    }
    result = get_ticket_visibility_scope(user_permissions, db_session)
    assert result["scope"] == "admin"
    assert result["allowed_ids"] == set()


def test_get_ticket_visibility_scope_manager(db_session: Session):
    """Employee without admin_actions but with subordinates returns manager scope."""
    manager = create_test_record(
        db_session,
        Employees,
        email="mgr_vis@example.com",
        first_name="Manager",
        last_name="Vis",
        display_name="Manager Vis",
    )
    sub = create_test_record(
        db_session,
        Employees,
        email="mgr_sub@example.com",
        first_name="Sub",
        last_name="Vis",
        display_name="Sub Vis",
        manager_employee_id=manager.employee_id,
    )
    db_session.commit()

    user_permissions = {
        "employee": {"employee_id": manager.employee_id, "email": manager.email},
        "permissions": [],
    }
    result = get_ticket_visibility_scope(user_permissions, db_session)
    assert result["scope"] == "manager"
    assert result["allowed_ids"] == {manager.employee_id, sub.employee_id}


def test_get_ticket_visibility_scope_user(db_session: Session):
    """Employee without admin_actions and without subordinates returns user scope."""
    emp = create_test_record(
        db_session,
        Employees,
        email="user_vis@example.com",
        first_name="User",
        last_name="Vis",
        display_name="User Vis",
    )
    db_session.commit()

    user_permissions = {
        "employee": {"employee_id": emp.employee_id, "email": emp.email},
        "permissions": [],
    }
    result = get_ticket_visibility_scope(user_permissions, db_session)
    assert result["scope"] == "user"
    assert result["allowed_ids"] == {emp.employee_id}


def test_get_ticket_visibility_scope_null_manager_falls_to_user(db_session: Session):
    """Employee with NULL manager_employee_id falls to user tier (not manager)."""
    emp = create_test_record(
        db_session,
        Employees,
        email="null_mgr@example.com",
        first_name="Null",
        last_name="Mgr",
        display_name="Null Mgr",
    )
    db_session.commit()

    user_permissions = {
        "employee": {"employee_id": emp.employee_id, "email": emp.email},
        "permissions": [],
    }
    result = get_ticket_visibility_scope(user_permissions, db_session)
    assert result["scope"] == "user"
    assert result["allowed_ids"] == {emp.employee_id}


# =============================================================================
# Integration: GET /tickets visibility (Tasks 2.1, 3.3-3.6)
# =============================================================================


def test_get_tickets_user_tier_only_own(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """User-tier employee sees only their own tickets."""
    create_test_record(
        db_session, Tickets, title="My Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other Ticket", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["created_by"] == current_employee.employee_id


def test_get_tickets_manager_tier_sees_team(
    client: TestClient,
    auth_headers: dict,
    manager_employee: Employees,
    subordinate_employee: Employees,
    second_subordinate: Employees,
    other_employee: Employees,
    db_session: Session,
    manager_auth_overrides,
):
    """Manager-tier employee sees own tickets + all subordinates' tickets."""
    create_test_record(
        db_session, Tickets, title="Manager Ticket", status=TicketStatus.TODO, created_by=manager_employee.employee_id
    )
    create_test_record(
        db_session,
        Tickets,
        title="Sub 1 Ticket",
        status=TicketStatus.TODO,
        created_by=subordinate_employee.employee_id,
    )
    create_test_record(
        db_session,
        Tickets,
        title="Sub 2 Ticket",
        status=TicketStatus.IN_PROGRESS,
        created_by=second_subordinate.employee_id,
    )
    create_test_record(
        db_session, Tickets, title="Other Ticket", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = {t["title"] for t in data}
    assert titles == {"Manager Ticket", "Sub 1 Ticket", "Sub 2 Ticket"}
    assert "Other Ticket" not in titles


def test_get_tickets_admin_tier_sees_all(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    admin_auth_overrides,
):
    """Admin-tier employee sees all tickets (no scope filter)."""
    create_test_record(
        db_session, Tickets, title="Admin Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other Ticket", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    titles = {t["title"] for t in data}
    assert "Admin Ticket" in titles
    assert "Other Ticket" in titles


def test_get_tickets_403_out_of_scope_assigned_to(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Non-admin requesting out-of-scope assigned_to gets 403."""
    response = client.get(f"/tickets?assigned_to={other_employee.employee_id}", headers=auth_headers)
    assert response.status_code == 403
    detail = response.json().get("detail", "")
    assert "outside" in detail.lower() or "permission" in detail.lower()


def test_get_tickets_403_out_of_scope_created_by(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """Non-admin requesting out-of-scope created_by gets 403."""
    response = client.get(f"/tickets?created_by={other_employee.employee_id}", headers=auth_headers)
    assert response.status_code == 403
    detail = response.json().get("detail", "")
    assert "outside" in detail.lower() or "permission" in detail.lower()


# =============================================================================
# Integration: GET /tickets/stats visibility (Tasks 2.2, 3.7)
# =============================================================================


def test_ticket_stats_manager_tier_aggregates_team(
    client: TestClient,
    auth_headers: dict,
    manager_employee: Employees,
    subordinate_employee: Employees,
    second_subordinate: Employees,
    other_employee: Employees,
    db_session: Session,
    manager_auth_overrides,
):
    """Manager-tier stats endpoint aggregates counts for self + all subordinates."""
    create_test_record(
        db_session, Tickets, title="Mgr", status=TicketStatus.TODO, created_by=manager_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Sub1", status=TicketStatus.DONE, created_by=subordinate_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Sub2", status=TicketStatus.TODO, created_by=second_subordinate.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3  # manager + 2 subs, excluding other_employee
    assert data["status_counts"].get("todo", 0) >= 2
    assert data["status_counts"].get("done", 0) >= 1


# =============================================================================
# Integration: GET /tickets/stats/users visibility (Tasks 2.3, 3.8)
# =============================================================================


def test_ticket_stats_users_scoped_to_visibility(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    auth_overrides,
):
    """stats/users returns only employees in user's visibility scope."""
    create_test_record(
        db_session, Tickets, title="My Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other Ticket", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets/stats/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    returned_ids = {u["employee_id"] for u in data}
    assert current_employee.employee_id in returned_ids
    assert other_employee.employee_id not in returned_ids


def test_ticket_stats_users_manager_sees_team(
    client: TestClient,
    auth_headers: dict,
    manager_employee: Employees,
    subordinate_employee: Employees,
    second_subordinate: Employees,
    other_employee: Employees,
    db_session: Session,
    manager_auth_overrides,
):
    """Manager-tier stats/users returns only subordinates (not self)."""
    create_test_record(
        db_session, Tickets, title="Mgr", status=TicketStatus.TODO, created_by=manager_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Sub1", status=TicketStatus.TODO, created_by=subordinate_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Sub2", status=TicketStatus.TODO, created_by=second_subordinate.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets/stats/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    returned_ids = {u["employee_id"] for u in data}
    # Manager sees only subordinates in the dropdown, not themselves
    assert returned_ids == {
        subordinate_employee.employee_id,
        second_subordinate.employee_id,
    }
    assert manager_employee.employee_id not in returned_ids
    assert other_employee.employee_id not in returned_ids


def test_ticket_stats_users_admin_sees_all(
    client: TestClient,
    auth_headers: dict,
    current_employee: Employees,
    other_employee: Employees,
    db_session: Session,
    admin_auth_overrides,
):
    """Admin-tier stats/users returns all employees with tickets."""
    create_test_record(
        db_session, Tickets, title="Admin Ticket", status=TicketStatus.TODO, created_by=current_employee.employee_id
    )
    create_test_record(
        db_session, Tickets, title="Other Ticket", status=TicketStatus.TODO, created_by=other_employee.employee_id
    )
    db_session.commit()

    response = client.get("/tickets/stats/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    returned_ids = {u["employee_id"] for u in data}
    assert current_employee.employee_id in returned_ids
    assert other_employee.employee_id in returned_ids
