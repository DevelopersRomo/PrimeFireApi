"""Fixtures for IT module tests."""

import pytest
from sqlmodel import Session, select

from main import app
from models.customers import Customers

IT_MODULE_KEYS = (
    "it_dashboard",
    "it_catalog",
    "it_licenses",
    "it_quotations",
    "it_templates",
    "it_documents",
)

FULL_PERMISSIONS = {
    "can_view": True,
    "can_create": True,
    "can_edit": True,
    "can_delete": True,
    "can_export": True,
    "admin_actions": True,
    "other_actions": True,
}


@pytest.fixture(autouse=True)
def it_admin_overrides():
    """Grant full permissions on all IT modules to the test caller."""
    from api.dependencies import get_current_employee_with_permissions

    def mock_permissions():
        return {
            "employee": {"employee_id": 1},
            "permissions": [{"module_key": key, "permissions": FULL_PERMISSIONS} for key in IT_MODULE_KEYS],
        }

    app.dependency_overrides[get_current_employee_with_permissions] = mock_permissions
    yield
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)


@pytest.fixture
def customer(db_session: Session) -> Customers:
    from models.employees import Employees

    existing = db_session.exec(select(Customers).where(Customers.company_name == "Speedy Gonzalez Welding")).first()
    if existing:
        return existing

    employee = db_session.exec(select(Employees)).first()
    if not employee:
        employee = Employees(email="creator@example.com")
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)

    customer = Customers(
        customer_type="commercial",
        company_name="Speedy Gonzalez Welding",
        primary_email="miranda@sgweld.com",
        created_by=employee.employee_id,
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def catalog_item_payload() -> dict:
    return {
        "item_type": "SERVICE",
        "name": "Website Development",
        "description": "Single Page + Contact Form",
        "unit": "PROJECT",
        "billing_cycle": "ONE_TIME",
        "unit_price": "450.00",
        "tax_rate": "0",
    }
