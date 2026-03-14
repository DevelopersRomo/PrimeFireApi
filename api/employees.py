from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from core.microsoft_graph import graph_client
from models.countries import Countries
from models.employees import EmployeeRoles, Employees, Roles
from schemas.employees import Employee, EmployeeRole, EmployeeRoleAssignment, EmployeeUpdate

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
    Get CountryId for a country name/code, creating it if it doesn't exist.
    Always stores standardized ISO codes.
    Returns (CountryId, was_created) tuple.
    CountryId is None if country_input is None or empty.
    """
    if not country_input or not country_input.strip():
        return None, False

    # Normalize to standard ISO code
    country_code = normalize_country_to_code(country_input.strip())
    if not country_code:
        return None, False

    # Try to find existing country by code
    existing_country = db.exec(select(Countries).filter(Countries.Name == country_code)).first()

    if existing_country:
        return existing_country.CountryId, False

    # Create new country with ISO code
    new_country = Countries(Name=country_code)
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country.CountryId, True


def employee_to_schema(db_employee: Employees) -> Employee:
    """Convert Employees model to Employee schema with computed country_name and roles."""
    roles = (
        [
            EmployeeRole(RoleId=role.RoleId, RoleName=role.RoleName, Description=role.Description)
            for role in db_employee.roles
        ]
        if db_employee.roles
        else []
    )

    return Employee(
        EmployeeId=db_employee.EmployeeId,
        FirstName=db_employee.FirstName,
        LastName=db_employee.LastName,
        DisplayName=db_employee.DisplayName,
        Title=db_employee.Title,
        Department=db_employee.Department,
        Office=db_employee.Office,
        Email=db_employee.Email,
        Phone=db_employee.Phone,
        MobilePhone=db_employee.MobilePhone,
        OfficePhone=db_employee.OfficePhone,
        Anydesk=db_employee.Anydesk,
        Manager=db_employee.Manager,
        ManagerEmail=db_employee.ManagerEmail,
        ManagerEmployeeId=db_employee.ManagerEmployeeId,
        StreetAddress=db_employee.StreetAddress,
        City=db_employee.City,
        State=db_employee.State,
        PostalCode=db_employee.PostalCode,
        CountryId=db_employee.CountryId,
        AzureOid=db_employee.AzureOid,
        AzureUpn=db_employee.AzureUpn,
        LastSyncedAt=db_employee.LastSyncedAt,
        country_name=db_employee.country.Name if db_employee.country else None,
        roles=roles,
    )


async def upsert_employee_from_microsoft_user(db: Session, ms_user: dict) -> Employees:
    """Create or update an employee in SQL from a Microsoft Graph user and return the SQL employee."""
    employee_data = graph_client.map_graph_user_to_employee(ms_user)

    graph_country = employee_data.pop("Country", None)
    country_id, _ = await get_or_create_country_id(db, graph_country) if graph_country else (None, False)
    employee_data["CountryId"] = country_id
    employee_data["LastSyncedAt"] = datetime.now()  # noqa: DTZ005

    azure_oid = employee_data.get("AzureOid")
    email = employee_data.get("Email")
    azure_upn = employee_data.get("AzureUpn")

    existing = None
    if azure_oid:
        existing = db.exec(select(Employees).where(Employees.AzureOid == azure_oid)).first()

    if not existing and (email or azure_upn):
        existing = db.exec(
            select(Employees).where(
                or_(
                    Employees.Email == email,
                    Employees.AzureUpn == azure_upn,
                    Employees.Email == azure_upn,
                    Employees.AzureUpn == email,
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
    """Resolve manager to a SQL EmployeeId, creating the manager in SQL from Microsoft if needed."""
    manager_email = manager_email.strip() if isinstance(manager_email, str) else manager_email
    manager_name = manager_name.strip() if isinstance(manager_name, str) else manager_name

    if manager_email:
        sql_manager = db.exec(
            select(Employees).where(or_(Employees.Email == manager_email, Employees.AzureUpn == manager_email))
        ).first()
        if sql_manager:
            return sql_manager.EmployeeId

        ms_manager = await graph_client.get_user(manager_email)
        sql_manager = await upsert_employee_from_microsoft_user(db, ms_manager)
        return sql_manager.EmployeeId

    if manager_name:
        sql_manager = db.exec(select(Employees).where(Employees.DisplayName == manager_name)).first()
        if sql_manager:
            return sql_manager.EmployeeId

        ms_manager = await graph_client.find_user_by_display_name(manager_name)
        if not ms_manager:
            return None

        manager_identifier = ms_manager.get("id") or ms_manager.get("userPrincipalName") or ms_manager.get("mail")
        if not manager_identifier:
            return None

        ms_manager_full = await graph_client.get_user(manager_identifier)
        sql_manager = await upsert_employee_from_microsoft_user(db, ms_manager_full)
        return sql_manager.EmployeeId

    return None


async def validate_and_resolve_manager(db: Session, employee_id: int, update_data: dict) -> dict:
    """
    Validate manager reference from PATCH payload.
    Manager can be resolved from SQL employees or Microsoft Graph.
    """
    has_manager_data = any(key in update_data for key in ("ManagerEmployeeId", "ManagerEmail", "Manager"))

    if not has_manager_data:
        return update_data

    manager_employee_id = update_data.get("ManagerEmployeeId")
    manager_email = update_data.get("ManagerEmail")
    manager_name = update_data.get("Manager")

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

        db_manager = db.exec(select(Employees).where(Employees.EmployeeId == manager_employee_id)).first()
        if not db_manager:
            raise HTTPException(status_code=400, detail="ManagerEmployeeId not found in SQL employees")

        update_data["ManagerEmployeeId"] = db_manager.EmployeeId
        update_data["Manager"] = manager_name or db_manager.DisplayName or db_manager.FirstName
        update_data["ManagerEmail"] = manager_email or db_manager.Email or db_manager.AzureUpn
        return update_data

    if manager_email:
        try:
            resolved_manager_id = await resolve_manager_employee_id(
                db, manager_email=manager_email, manager_name=manager_name
            )
            if not resolved_manager_id:
                raise HTTPException(
                    status_code=400, detail="ManagerEmail is invalid. Manager must exist in Microsoft or SQL employees."
                )
            if resolved_manager_id == employee_id:
                raise HTTPException(status_code=400, detail="Employee cannot be their own manager")

            db_manager = db.exec(select(Employees).where(Employees.EmployeeId == resolved_manager_id)).first()
            if not db_manager:
                raise HTTPException(status_code=400, detail="Manager could not be resolved in SQL")

            update_data["ManagerEmployeeId"] = db_manager.EmployeeId
            update_data["Manager"] = manager_name or db_manager.DisplayName or db_manager.FirstName
            update_data["ManagerEmail"] = db_manager.Email or db_manager.AzureUpn or manager_email
            return update_data
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400, detail="ManagerEmail is invalid. Manager must exist in Microsoft or SQL employees."
            )

    if manager_name:
        try:
            resolved_manager_id = await resolve_manager_employee_id(db, manager_name=manager_name)
            if not resolved_manager_id:
                raise HTTPException(status_code=400, detail="Manager must exist in Microsoft or SQL employees")
            if resolved_manager_id == employee_id:
                raise HTTPException(status_code=400, detail="Employee cannot be their own manager")

            db_manager = db.exec(select(Employees).where(Employees.EmployeeId == resolved_manager_id)).first()
            if not db_manager:
                raise HTTPException(status_code=400, detail="Manager could not be resolved in SQL")

            update_data["ManagerEmployeeId"] = db_manager.EmployeeId
            update_data["Manager"] = db_manager.DisplayName or manager_name
            update_data["ManagerEmail"] = db_manager.Email or db_manager.AzureUpn
            return update_data
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Manager must exist in Microsoft or SQL employees")

    update_data["ManagerEmployeeId"] = None
    update_data["Manager"] = None
    update_data["ManagerEmail"] = None
    return update_data


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[Employee])
def get_employees(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    employees = db.exec(select(Employees).join(Countries, isouter=True).options(selectinload(Employees.roles))).all()
    return [employee_to_schema(emp) for emp in employees]


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_employee = db.exec(
        select(Employees)
        .join(Countries, isouter=True)
        .options(selectinload(Employees.roles))
        .filter(Employees.EmployeeId == employee_id)
    ).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_to_schema(db_employee)


# ----------------------------
# 📌 UPDATE (SIEMPRE SINCRONIZA CON MICROSOFT)
# ----------------------------
@router.patch("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """
    Update employee in local database and sync to Microsoft 365 if possible.
    Always attempts Microsoft sync, but continues if AzureOid is missing or sync fails.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)
    update_data = await validate_and_resolve_manager(db, employee_id, update_data)

    # Update local database first
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    # Always attempt to sync to Microsoft (if employee has AzureOid)
    if db_employee.AzureOid:
        try:
            graph_data = graph_client.map_employee_to_graph_user(update_data)
            if graph_data:
                await graph_client.update_user(db_employee.AzureOid, graph_data)

            manager_updated_in_payload = any(
                key in update_data for key in ("ManagerEmployeeId", "ManagerEmail", "Manager")
            )
            if manager_updated_in_payload:
                if db_employee.ManagerEmployeeId is None:
                    await graph_client.clear_user_manager(db_employee.AzureOid)
                else:
                    db_manager = db.exec(
                        select(Employees).where(Employees.EmployeeId == db_employee.ManagerEmployeeId)
                    ).first()
                    if db_manager:
                        manager_identifier = db_manager.AzureOid or db_manager.AzureUpn or db_manager.Email
                        if manager_identifier:
                            await graph_client.set_user_manager(db_employee.AzureOid, manager_identifier)

            db_employee.LastSyncedAt = datetime.now()  # noqa: DTZ005
        except Exception:
            # Log the error but don't fail the entire operation
            pass
            # Continue without failing - local update still succeeds

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
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if role exists
    db_role = db.exec(select(Roles).filter(Roles.RoleId == role_assignment.RoleId)).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if employee already has this role
    existing_assignment = db.exec(
        select(EmployeeRoles)
        .filter(EmployeeRoles.EmployeeId == employee_id)
        .filter(EmployeeRoles.RoleId == role_assignment.RoleId)
    ).first()

    if existing_assignment:
        raise HTTPException(status_code=400, detail="Employee already has this role")

    # Create new role assignment
    employee_role = EmployeeRoles(EmployeeId=employee_id, RoleId=role_assignment.RoleId)
    db.add(employee_role)
    db.commit()

    # Return updated employee with roles
    return get_employee(employee_id, db, _auth)


@router.delete("/{employee_id}/roles/{role_id}", response_model=Employee)
async def remove_role_from_employee(
    employee_id: int, role_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)
):
    """Remove a role from an employee."""
    # Check if assignment exists
    assignment = db.exec(
        select(EmployeeRoles).filter(EmployeeRoles.EmployeeId == employee_id).filter(EmployeeRoles.RoleId == role_id)
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Employee does not have this role")

    # Remove assignment
    db.delete(assignment)
    db.commit()

    # Return updated employee with roles
    return get_employee(employee_id, db, _auth)


@router.get("/{employee_id}/roles", response_model=list[EmployeeRole])
async def get_employee_roles(employee_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """Get all roles for a specific employee."""
    # Check if employee exists
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get roles through the relationship
    return [
        EmployeeRole(RoleId=role.RoleId, RoleName=role.RoleName, Description=role.Description)
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
            employee_data["LastSyncedAt"] = datetime.now()  # noqa: DTZ005
            employee_data["CountryId"] = country_id

            manager_email = employee_data.get("ManagerEmail")
            manager_name = employee_data.get("Manager")
            employee_data["ManagerEmployeeId"] = await resolve_manager_employee_id(
                db, manager_email=manager_email, manager_name=manager_name
            )

            # Check if employee exists by AzureOid
            existing = db.exec(select(Employees).filter(Employees.AzureOid == employee_data["AzureOid"])).first()

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
    Requires employee to have AzureOid.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not db_employee.AzureOid:
        raise HTTPException(status_code=400, detail="Employee does not have AzureOid. Cannot sync to Microsoft 365.")

    try:
        # Convert employee to Graph format
        employee_dict = db_employee.model_dump()
        graph_data = graph_client.map_employee_to_graph_user(employee_dict)

        if not graph_data:
            raise HTTPException(status_code=400, detail="No data to sync to Microsoft 365")

        # Update in Microsoft
        await graph_client.update_user(db_employee.AzureOid, graph_data)

        # Update sync timestamp
        db_employee.LastSyncedAt = datetime.now()  # noqa: DTZ005
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
    Fetch and sync a single employee from Microsoft 365 by their AzureOid.
    Updates local database with Microsoft data.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not db_employee.AzureOid:
        raise HTTPException(status_code=400, detail="Employee does not have AzureOid. Cannot sync from Microsoft 365.")

    try:
        # Fetch from Microsoft
        ms_user = await graph_client.get_user(db_employee.AzureOid)
        employee_data = graph_client.map_graph_user_to_employee(ms_user)

        # Update local employee
        for key, value in employee_data.items():
            if value is not None:
                setattr(db_employee, key, value)

        manager_email = employee_data.get("ManagerEmail")
        manager_name = employee_data.get("Manager")
        db_employee.ManagerEmployeeId = await resolve_manager_employee_id(
            db, manager_email=manager_email, manager_name=manager_name
        )

        db_employee.LastSyncedAt = datetime.now()  # noqa: DTZ005
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
