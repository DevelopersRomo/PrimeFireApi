import logging
from datetime import datetime
import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from core.microsoft_graph import graph_client
from models.countries import Countries
from models.employees import EmployeeRoles, Employees, Roles
from schemas.employees import Employee, EmployeeRole, EmployeeRoleAssignment, EmployeeUpdate
from schemas.pagination import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def normalize_country_to_code(country_name: str) -> str | None:
    """Convert country names or codes to standard ISO 3166-1 alpha-2 codes."""
    if not country_name or not country_name.strip():
        return None

    country_name = country_name.strip().upper()

    # Direct mapping for common countries
    country_map = {
        # United States variations
        "UNITED STATES": "US",
        "USA": "US",
        "UNITED STATES OF AMERICA": "US",
        "US": "US",
        "AMERICA": "US",
        # Puerto Rico
        "PUERTO RICO": "PR",
        "PR": "PR",
        # Dominican Republic variations
        "REPÚBLICA DOMINICANA": "DO",
        "DOMINICAN REPUBLIC": "DO",
        "REPUBLICA DOMINICANA": "DO",
        "DO": "DO",
        # Mexico
        "MEXICO": "MX",
        "MÉXICO": "MX",
        "MX": "MX",
        # Add more countries as needed
        "CANADA": "CA",
        "SPAIN": "ES",
        "FRANCE": "FR",
        "GERMANY": "DE",
        "ITALY": "IT",
        "UNITED KINGDOM": "GB",
        "UK": "GB",
    }

    return country_map.get(country_name)


async def get_or_create_country_id(db: Session, country_input: str) -> tuple[int | None, bool]:
    """
    Get country_id for a country name/code, creating it if it doesn't exist.
    Always stores standardized ISO codes.
    Returns (country_id, was_created) tuple.
    country_id is None if country_input is None or empty.
    """
    if not country_input or not country_input.strip():
        return None, False

    # Normalize to standard ISO code
    country_code = normalize_country_to_code(country_input.strip())
    if not country_code:
        return None, False

    # Try to find existing country by code
    existing_country = db.exec(select(Countries).filter(Countries.name == country_code)).first()

    if existing_country:
        return existing_country.country_id, False

    # Create new country with ISO code
    new_country = Countries(name=country_code)
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country.country_id, True


def employee_to_schema(db_employee: Employees) -> Employee:
    """Convert Employees model to Employee schema with computed country_name and roles."""
    roles = (
        [
            EmployeeRole(role_id=role.role_id, role_name=role.role_name, description=role.description)
            for role in db_employee.roles
        ]
        if db_employee.roles
        else []
    )

    return Employee(
        employee_id=db_employee.employee_id,
        first_name=db_employee.first_name,
        last_name=db_employee.last_name,
        display_name=db_employee.display_name,
        title=db_employee.title,
        department=db_employee.department,
        office=db_employee.office,
        email=db_employee.email,
        phone=db_employee.phone,
        mobile_phone=db_employee.mobile_phone,
        office_phone=db_employee.office_phone,
        anydesk=db_employee.anydesk,
        manager=db_employee.manager,
        manager_email=db_employee.manager_email,
        manager_employee_id=db_employee.manager_employee_id,
        street_address=db_employee.street_address,
        city=db_employee.city,
        state=db_employee.state,
        postal_code=db_employee.postal_code,
        country_id=db_employee.country_id,
        azure_oid=db_employee.azure_oid,
        azure_upn=db_employee.azure_upn,
        last_synced_at=db_employee.last_synced_at,
        country_name=db_employee.country.name if db_employee.country else None,
        roles=roles,
        has_license=False,
        has_active_license=False,
    )


async def enrich_employee_license_flags(schema: Employee, azure_oid: str | None) -> Employee:
    if not azure_oid:
        schema.has_license = False
        schema.has_active_license = False
        return schema

    try:
        license_details = await graph_client.get_user_license_details(azure_oid)
        has_m365_license = len(license_details) > 0
        schema.has_license = has_m365_license
        schema.has_active_license = has_m365_license
    except Exception:
        logger.exception("Failed to load Microsoft 365 licenses for employee azure_oid=%s", azure_oid)
        schema.has_license = False
        schema.has_active_license = False

    return schema


async def upsert_employee_from_microsoft_user(db: Session, ms_user: dict) -> Employees:
    """Create or update an employee in SQL from a Microsoft Graph user and return the SQL employee."""
    employee_data = graph_client.map_graph_user_to_employee(ms_user)

    graph_country = employee_data.pop("country", None)
    country_id, _ = await get_or_create_country_id(db, graph_country) if graph_country else (None, False)
    employee_data["country_id"] = country_id
    employee_data["last_synced_at"] = datetime.now()  # noqa: DTZ005

    azure_oid = employee_data.get("azure_oid")
    email = employee_data.get("email")
    azure_upn = employee_data.get("azure_upn")

    existing = None
    if azure_oid:
        existing = db.exec(select(Employees).where(Employees.azure_oid == azure_oid)).first()

    if not existing and (email or azure_upn):
        existing = db.exec(
            select(Employees).where(
                or_(
                    Employees.email == email,
                    Employees.azure_upn == azure_upn,
                    Employees.email == azure_upn,
                    Employees.azure_upn == email,
                )
            )
        ).first()

    if existing:
        for key, value in employee_data.items():
            if value is not None:
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_employee = Employees(**employee_data)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


async def resolve_manager_employee_id(
    db: Session, manager_email: str | None = None, manager_name: str | None = None
) -> int | None:
    """Resolve manager to a SQL employee_id, creating the manager in SQL from Microsoft if needed."""
    manager_email = manager_email.strip() if isinstance(manager_email, str) else manager_email
    manager_name = manager_name.strip() if isinstance(manager_name, str) else manager_name

    if manager_email:
        sql_manager = db.exec(
            select(Employees).where(or_(Employees.email == manager_email, Employees.azure_upn == manager_email))
        ).first()
        if sql_manager:
            return sql_manager.employee_id

        ms_manager = await graph_client.get_user(manager_email)
        sql_manager = await upsert_employee_from_microsoft_user(db, ms_manager)
        return sql_manager.employee_id

    if manager_name:
        sql_manager = db.exec(select(Employees).where(Employees.display_name == manager_name)).first()
        if sql_manager:
            return sql_manager.employee_id

        ms_manager = await graph_client.find_user_by_display_name(manager_name)
        if not ms_manager:
            return None

        manager_identifier = ms_manager.get("id") or ms_manager.get("userPrincipalName") or ms_manager.get("mail")
        if not manager_identifier:
            return None

        ms_manager_full = await graph_client.get_user(manager_identifier)
        sql_manager = await upsert_employee_from_microsoft_user(db, ms_manager_full)
        return sql_manager.employee_id

    return None


async def validate_and_resolve_manager(db: Session, employee_id: int, update_data: dict) -> dict:
    """
    Validate manager reference from PATCH payload.
    Manager can be resolved from SQL employees or Microsoft Graph.
    """
    has_manager_data = any(key in update_data for key in ("manager_employee_id", "manager_email", "manager"))

    if not has_manager_data:
        return update_data

    manager_employee_id = update_data.get("manager_employee_id")
    manager_email = update_data.get("manager_email")
    manager_name = update_data.get("manager")

    if isinstance(manager_email, str):
        manager_email = manager_email.strip()
        if not manager_email:
            manager_email = None

    if isinstance(manager_name, str):
        manager_name = manager_name.strip()
        if not manager_name:
            manager_name = None

    if manager_employee_id is not None:
        if manager_employee_id == employee_id:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")

        db_manager = db.exec(select(Employees).where(Employees.employee_id == manager_employee_id)).first()
        if not db_manager:
            raise HTTPException(status_code=400, detail="manager_employee_id not found in SQL employees")

        update_data["manager_employee_id"] = db_manager.employee_id
        update_data["manager"] = manager_name or db_manager.display_name or db_manager.first_name
        update_data["manager_email"] = manager_email or db_manager.email or db_manager.azure_upn
        return update_data

    if manager_email:
        try:
            resolved_manager_id = await resolve_manager_employee_id(
                db, manager_email=manager_email, manager_name=manager_name
            )
            if not resolved_manager_id:
                raise HTTPException(
                    status_code=400, detail="manager_email is invalid. Manager must exist in Microsoft or SQL employees."
                )
            if resolved_manager_id == employee_id:
                raise HTTPException(status_code=400, detail="Employee cannot be their own manager")

            db_manager = db.exec(select(Employees).where(Employees.employee_id == resolved_manager_id)).first()
            if not db_manager:
                raise HTTPException(status_code=400, detail="Manager could not be resolved in SQL")

            update_data["manager_employee_id"] = db_manager.employee_id
            update_data["manager"] = manager_name or db_manager.display_name or db_manager.first_name
            update_data["manager_email"] = db_manager.email or db_manager.azure_upn or manager_email
            return update_data
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400, detail="manager_email is invalid. Manager must exist in Microsoft or SQL employees."
            )

    if manager_name:
        try:
            resolved_manager_id = await resolve_manager_employee_id(db, manager_name=manager_name)
            if not resolved_manager_id:
                raise HTTPException(status_code=400, detail="Manager must exist in Microsoft or SQL employees")
            if resolved_manager_id == employee_id:
                raise HTTPException(status_code=400, detail="Employee cannot be their own manager")

            db_manager = db.exec(select(Employees).where(Employees.employee_id == resolved_manager_id)).first()
            if not db_manager:
                raise HTTPException(status_code=400, detail="Manager could not be resolved in SQL")

            update_data["manager_employee_id"] = db_manager.employee_id
            update_data["manager"] = db_manager.display_name or manager_name
            update_data["manager_email"] = db_manager.email or db_manager.azure_upn
            return update_data
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Manager must exist in Microsoft or SQL employees")

    update_data["manager_employee_id"] = None
    update_data["manager"] = None
    update_data["manager_email"] = None
    return update_data


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[Employee] | PaginatedResponse[Employee])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    include_license_status: bool = Query(False),
    license_filter: str = Query("all", pattern="^(all|with_license|without_license|with_active_license)$"),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    statement = (
        select(Employees)
        .join(Countries, isouter=True)
        .options(selectinload(Employees.roles))
        .order_by(Employees.display_name, Employees.employee_id)
    )
    employees = db.exec(statement).all()
    if include_license_status:
        items = await asyncio.gather(
            *[enrich_employee_license_flags(employee_to_schema(emp), emp.azure_oid) for emp in employees]
        )

        if license_filter == "with_license":
            items = [item for item in items if item.has_license]
        elif license_filter == "without_license":
            items = [item for item in items if not item.has_license]
        elif license_filter == "with_active_license":
            items = [item for item in items if item.has_active_license]
    else:
        items = [employee_to_schema(emp) for emp in employees]

    total = len(items)
    items = items[skip : skip + limit]

    if not with_meta:
        return items

    return PaginatedResponse[Employee](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_employee = db.exec(
        select(Employees)
        .join(Countries, isouter=True)
        .options(selectinload(Employees.roles))
        .filter(Employees.employee_id == employee_id)
    ).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return await enrich_employee_license_flags(employee_to_schema(db_employee), db_employee.azure_oid)


# ----------------------------
# 📌 UPDATE (SIEMPRE SINCRONIZA CON MICROSOFT)
# ----------------------------
@router.patch("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """
    Update employee in local database and sync to Microsoft 365 if possible.
    Always attempts Microsoft sync, but continues if azure_oid is missing or sync fails.
    """
    db_employee = db.exec(select(Employees).filter(Employees.employee_id == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)
    update_data = await validate_and_resolve_manager(db, employee_id, update_data)

    # Update local database first
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    # Always attempt to sync to Microsoft (if employee has azure_oid)
    synced = False
    if db_employee.azure_oid:
        try:
            # Resolve country_id to ISO code for Microsoft Graph
            if "country_id" in update_data and update_data["country_id"] is not None:
                country = db.exec(
                    select(Countries).where(Countries.country_id == update_data["country_id"])
                ).first()
                if country:
                    update_data["country"] = country.name

            graph_data = graph_client.map_employee_to_graph_user(update_data)
            if graph_data:
                await graph_client.update_user(db_employee.azure_oid, graph_data)
                synced = True

            manager_updated_in_payload = any(
                key in update_data for key in ("manager_employee_id", "manager_email", "manager")
            )
            if manager_updated_in_payload:
                if db_employee.manager_employee_id is None:
                    await graph_client.clear_user_manager(db_employee.azure_oid)
                else:
                    db_manager = db.exec(
                        select(Employees).where(Employees.employee_id == db_employee.manager_employee_id)
                    ).first()
                    if db_manager:
                        manager_identifier = db_manager.azure_oid or db_manager.azure_upn or db_manager.email
                        if manager_identifier:
                            await graph_client.set_user_manager(db_employee.azure_oid, manager_identifier)
                synced = True

            if synced:
                db_employee.last_synced_at = datetime.now()  # noqa: DTZ005
        except Exception as e:
            logger.exception(
                "Failed to sync employee %d (azure_oid=%s) to Microsoft 365: %s",
                employee_id,
                db_employee.azure_oid,
                e,
            )
            # Continue without failing — local update still succeeds

    db.commit()
    db.refresh(db_employee)
    return employee_to_schema(db_employee)


# ----------------------------
# 📌 EMPLOYEE ROLES MANAGEMENT
# ----------------------------
@router.post("/{employee_id}/roles", response_model=Employee)
async def assign_role_to_employee(
    employee_id: int,
    role_assignment: EmployeeRoleAssignment,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication),
):
    """Assign a role to an employee."""
    # Check if employee exists
    db_employee = db.exec(select(Employees).filter(Employees.employee_id == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if role exists
    db_role = db.exec(select(Roles).filter(Roles.role_id == role_assignment.role_id)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if employee already has this role
    existing_assignment = db.exec(
        select(EmployeeRoles)
        .filter(EmployeeRoles.employee_id == employee_id)
        .filter(EmployeeRoles.role_id == role_assignment.role_id)
    ).first()

    if existing_assignment:
        raise HTTPException(status_code=400, detail="Employee already has this role")

    # Create new role assignment
    employee_role = EmployeeRoles(employee_id=employee_id, role_id=role_assignment.role_id)
    db.add(employee_role)
    db.commit()

    # Return updated employee with roles
    return await get_employee(employee_id, db, _auth)


@router.delete("/{employee_id}/roles/{role_id}", response_model=Employee)
async def remove_role_from_employee(
    employee_id: int, role_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """Remove a role from an employee."""
    # Check if assignment exists
    assignment = db.exec(
        select(EmployeeRoles).filter(EmployeeRoles.employee_id == employee_id).filter(EmployeeRoles.role_id == role_id)
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Employee does not have this role")

    # Remove assignment
    db.delete(assignment)
    db.commit()

    # Return updated employee with roles
    return await get_employee(employee_id, db, _auth)


@router.get("/{employee_id}/roles", response_model=list[EmployeeRole])
async def get_employee_roles(employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get all roles for a specific employee."""
    # Check if employee exists
    db_employee = db.exec(select(Employees).filter(Employees.employee_id == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get roles through the relationship
    return [
        EmployeeRole(role_id=role.role_id, role_name=role.role_name, description=role.description)
        for role in db_employee.roles
    ]


# ----------------------------
# 📌 MICROSOFT SYNC - GET ALL FROM MICROSOFT
# ----------------------------
@router.get("/sync/from-microsoft", response_model=list[Employee])
async def sync_from_microsoft(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """
    Sync all users from Microsoft 365 to local database.
    Creates new employees if they don't exist, updates existing ones.
    """
    try:
        ms_users = await graph_client.get_all_users()
        synced_employees = []

        for ms_user in ms_users:
            # Filter only PrimeFire domains
            email = ms_user.get("userPrincipalName") or ms_user.get("mail")
            if not email:
                continue  # Skip users without email

            # Extract domain and check if it's PrimeFire
            domain = email.lower().split("@")[-1] if "@" in email else ""
            domain_parts = domain.split(".")
            if not any(part == "primefire" for part in domain_parts):
                continue  # Skip non-PrimeFire users

            # Get country from Graph user data
            graph_country = ms_user.get("country")
            country_id, _ = await get_or_create_country_id(db, graph_country) if graph_country else (None, False)

            employee_data = graph_client.map_graph_user_to_employee(ms_user)
            employee_data["last_synced_at"] = datetime.now()  # noqa: DTZ005
            employee_data["country_id"] = country_id

            manager_email = employee_data.get("manager_email")
            manager_name = employee_data.get("manager")
            employee_data["manager_employee_id"] = await resolve_manager_employee_id(
                db, manager_email=manager_email, manager_name=manager_name
            )

            # Check if employee exists by azure_oid
            existing = db.exec(select(Employees).filter(Employees.azure_oid == employee_data["azure_oid"])).first()

            if existing:
                # Update existing employee
                for key, value in employee_data.items():
                    if value is not None:
                        setattr(existing, key, value)
                db.commit()
                db.refresh(existing)
                synced_employees.append(existing)
            else:
                # Create new employee
                new_employee = Employees(**employee_data)
                db.add(new_employee)
                db.commit()
                db.refresh(new_employee)
                synced_employees.append(new_employee)

        return synced_employees

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync from Microsoft 365: {e!s}")


# ----------------------------
# 📌 MICROSOFT SYNC - PUSH EMPLOYEE TO MICROSOFT
# ----------------------------
@router.put("/{employee_id}/sync-to-microsoft", response_model=Employee)
async def sync_employee_to_microsoft(
    employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """
    Sync a specific employee from local database to Microsoft 365.
    Requires employee to have azure_oid.
    """
    db_employee = db.exec(select(Employees).filter(Employees.employee_id == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not db_employee.azure_oid:
        raise HTTPException(status_code=400, detail="Employee does not have azure_oid. Cannot sync to Microsoft 365.")

    try:
        # Convert employee to Graph format
        employee_dict = db_employee.model_dump()
        graph_data = graph_client.map_employee_to_graph_user(employee_dict)

        if not graph_data:
            raise HTTPException(status_code=400, detail="No data to sync to Microsoft 365")

        # Update in Microsoft
        await graph_client.update_user(db_employee.azure_oid, graph_data)

        # Update sync timestamp
        db_employee.last_synced_at = datetime.now()  # noqa: DTZ005
        db.commit()
        db.refresh(db_employee)

        return db_employee

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync to Microsoft 365: {e!s}")


# ----------------------------
# 📌 MICROSOFT SYNC - GET SINGLE USER FROM MICROSOFT
# ----------------------------
@router.get("/{employee_id}/sync-from-microsoft", response_model=Employee)
async def sync_single_employee_from_microsoft(
    employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """
    Fetch and sync a single employee from Microsoft 365 by their azure_oid.
    Updates local database with Microsoft data.
    """
    db_employee = db.exec(select(Employees).filter(Employees.employee_id == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not db_employee.azure_oid:
        raise HTTPException(status_code=400, detail="Employee does not have azure_oid. Cannot sync from Microsoft 365.")

    try:
        # Fetch from Microsoft
        ms_user = await graph_client.get_user(db_employee.azure_oid)
        employee_data = graph_client.map_graph_user_to_employee(ms_user)

        # Update local employee
        for key, value in employee_data.items():
            if value is not None:
                setattr(db_employee, key, value)

        manager_email = employee_data.get("manager_email")
        manager_name = employee_data.get("manager")
        db_employee.manager_employee_id = await resolve_manager_employee_id(
            db, manager_email=manager_email, manager_name=manager_name
        )

        db_employee.last_synced_at = datetime.now()  # noqa: DTZ005
        db.commit()
        db.refresh(db_employee)

        return db_employee

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync from Microsoft 365: {e!s}")


# ----------------------------
# 📌 TRIGGER MANUAL SYNC (Background)
# ----------------------------
@router.post("/sync/trigger")
async def trigger_background_sync(background_tasks: BackgroundTasks, _auth=Depends(require_authentication)):
    """
    Trigger a manual background sync from Microsoft 365.
    Returns immediately while sync runs in background.
    """
    from core.background_tasks import sync_scheduler

    # Add sync task to background
    background_tasks.add_task(sync_scheduler.sync_employees_from_microsoft)

    return {
        "message": "Sync triggered successfully",
        "status": "running in background",
        "last_sync": sync_scheduler.last_sync,
    }


# ----------------------------
# 📌 GET SYNC STATUS
# ----------------------------
@router.get("/sync/status")
async def get_sync_status(_auth=Depends(require_authentication)):
    """Get the status of the employee sync scheduler."""
    from core.background_tasks import sync_scheduler

    return {
        "is_running": sync_scheduler.is_running,
        "last_sync": sync_scheduler.last_sync,
        "sync_interval_hours": sync_scheduler.sync_interval_hours,
    }
