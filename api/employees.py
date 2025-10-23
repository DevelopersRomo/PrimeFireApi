from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.employees import Employees, Roles, EmployeeRoles
from models.countries import Countries
from schemas.employees import Employee, EmployeeUpdate, EmployeeRoleAssignment, EmployeeRole
from core.microsoft_graph import graph_client

router = APIRouter()

def normalize_country_to_code(country_name: str) -> Optional[str]:
    """
    Convert country names or codes to standard ISO 3166-1 alpha-2 codes.
    """
    if not country_name or not country_name.strip():
        return None

    country_name = country_name.strip().upper()

    # Direct mapping for common countries
    country_map = {
        # United States variations
        'UNITED STATES': 'US',
        'USA': 'US',
        'UNITED STATES OF AMERICA': 'US',
        'US': 'US',
        'AMERICA': 'US',

        # Puerto Rico
        'PUERTO RICO': 'PR',
        'PR': 'PR',

        # Dominican Republic variations
        'REPÚBLICA DOMINICANA': 'DO',
        'DOMINICAN REPUBLIC': 'DO',
        'REPUBLICA DOMINICANA': 'DO',
        'DO': 'DO',

        # Mexico
        'MEXICO': 'MX',
        'MÉXICO': 'MX',
        'MX': 'MX',

        # Add more countries as needed
        'CANADA': 'CA',
        'SPAIN': 'ES',
        'FRANCE': 'FR',
        'GERMANY': 'DE',
        'ITALY': 'IT',
        'UNITED KINGDOM': 'GB',
        'UK': 'GB',
    }

    return country_map.get(country_name)

async def get_or_create_country_id(db: Session, country_input: str) -> tuple[Optional[int], bool]:
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
    existing_country = db.exec(
        select(Countries).filter(Countries.Name == country_code)
    ).first()

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
    roles = [
        EmployeeRole(
            RoleId=role.RoleId,
            RoleName=role.RoleName,
            Description=role.Description
        )
        for role in db_employee.roles
    ] if db_employee.roles else []

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
        StreetAddress=db_employee.StreetAddress,
        City=db_employee.City,
        State=db_employee.State,
        PostalCode=db_employee.PostalCode,
        CountryId=db_employee.CountryId,
        AzureOid=db_employee.AzureOid,
        AzureUpn=db_employee.AzureUpn,
        LastSyncedAt=db_employee.LastSyncedAt,
        country_name=db_employee.country.Name if db_employee.country else None,
        roles=roles
    )

# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("/", response_model=List[Employee])
def get_employees(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    employees = db.exec(
        select(Employees)
        .join(Countries, isouter=True)
        .options(selectinload(Employees.roles))
    ).all()
    return [employee_to_schema(emp) for emp in employees]

# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
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
@router.patch("/{employee_id}")
async def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """
    Update employee in local database and sync to Microsoft 365 if possible.
    Always attempts Microsoft sync, but continues if AzureOid is missing or sync fails.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)

    # Update local database first
    for key, value in update_data.items():
        setattr(db_employee, key, value)

    # Always attempt to sync to Microsoft (if employee has AzureOid)
    sync_success = False
    if db_employee.AzureOid:
        try:
            graph_data = graph_client.map_employee_to_graph_user(update_data)
            if graph_data:
                await graph_client.update_user(db_employee.AzureOid, graph_data)
                db_employee.LastSyncedAt = datetime.now()
                sync_success = True
        except Exception as e:
            # Log the error but don't fail the entire operation
            print(f"Warning: Failed to sync employee {employee_id} to Microsoft 365: {str(e)}")
            # Continue without failing - local update still succeeds

    db.commit()
    db.refresh(db_employee)

    # Add sync status to response (optional - for debugging)
    response = db_employee.model_dump()
    response["_sync_status"] = "successful" if sync_success else "not_synced"
    if not db_employee.AzureOid:
        response["_sync_status"] = "no_azure_oid"

        return response

# ----------------------------
# 📌 EMPLOYEE ROLES MANAGEMENT
# ----------------------------
@router.post("/{employee_id}/roles", response_model=Employee)
async def assign_role_to_employee(
    employee_id: int,
    role_assignment: EmployeeRoleAssignment,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
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
    employee_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Remove a role from an employee."""
    # Check if assignment exists
    assignment = db.exec(
        select(EmployeeRoles)
        .filter(EmployeeRoles.EmployeeId == employee_id)
        .filter(EmployeeRoles.RoleId == role_id)
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Employee does not have this role")

    # Remove assignment
    db.delete(assignment)
    db.commit()

    # Return updated employee with roles
    return get_employee(employee_id, db, _auth)

@router.get("/{employee_id}/roles", response_model=List[EmployeeRole])
async def get_employee_roles(
    employee_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Get all roles for a specific employee."""
    # Check if employee exists
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Get roles through the relationship
    roles = [
        EmployeeRole(
            RoleId=role.RoleId,
            RoleName=role.RoleName,
            Description=role.Description
        )
        for role in db_employee.roles
    ]

    return roles

# ----------------------------
# 📌 MICROSOFT SYNC - GET ALL FROM MICROSOFT
# ----------------------------
@router.get("/sync/from-microsoft", response_model=List[Employee])
async def sync_from_microsoft(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
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
            domain = email.lower().split('@')[-1] if '@' in email else ''
            domain_parts = domain.split('.')
            if not any('primefire' == part for part in domain_parts):
                continue  # Skip non-PrimeFire users

            # Get country from Graph user data
            graph_country = ms_user.get("country")
            country_id, _ = await get_or_create_country_id(db, graph_country) if graph_country else (None, False)

            employee_data = graph_client.map_graph_user_to_employee(ms_user)
            employee_data["LastSyncedAt"] = datetime.now()
            employee_data["CountryId"] = country_id

            # Check if employee exists by AzureOid
            existing = db.exec(
                select(Employees).filter(Employees.AzureOid == employee_data["AzureOid"])
            ).first()

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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync from Microsoft 365: {str(e)}"
        )

# ----------------------------
# 📌 MICROSOFT SYNC - PUSH EMPLOYEE TO MICROSOFT
# ----------------------------
@router.put("/{employee_id}/sync-to-microsoft", response_model=Employee)
async def sync_employee_to_microsoft(
    employee_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """
    Sync a specific employee from local database to Microsoft 365.
    Requires employee to have AzureOid.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not db_employee.AzureOid:
        raise HTTPException(
            status_code=400,
            detail="Employee does not have AzureOid. Cannot sync to Microsoft 365."
        )
    
    try:
        # Convert employee to Graph format
        employee_dict = db_employee.model_dump()
        graph_data = graph_client.map_employee_to_graph_user(employee_dict)
        
        if not graph_data:
            raise HTTPException(
                status_code=400,
                detail="No data to sync to Microsoft 365"
            )
        
        # Update in Microsoft
        await graph_client.update_user(db_employee.AzureOid, graph_data)
        
        # Update sync timestamp
        db_employee.LastSyncedAt = datetime.now()
        db.commit()
        db.refresh(db_employee)
        
        return db_employee
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync to Microsoft 365: {str(e)}"
        )

# ----------------------------
# 📌 MICROSOFT SYNC - GET SINGLE USER FROM MICROSOFT
# ----------------------------
@router.get("/{employee_id}/sync-from-microsoft", response_model=Employee)
async def sync_single_employee_from_microsoft(
    employee_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """
    Fetch and sync a single employee from Microsoft 365 by their AzureOid.
    Updates local database with Microsoft data.
    """
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if not db_employee.AzureOid:
        raise HTTPException(
            status_code=400,
            detail="Employee does not have AzureOid. Cannot sync from Microsoft 365."
        )
    
    try:
        # Fetch from Microsoft
        ms_user = await graph_client.get_user(db_employee.AzureOid)
        employee_data = graph_client.map_graph_user_to_employee(ms_user)
        
        # Update local employee
        for key, value in employee_data.items():
            if value is not None:
                setattr(db_employee, key, value)
        
        db_employee.LastSyncedAt = datetime.now()
        db.commit()
        db.refresh(db_employee)
        
        return db_employee
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync from Microsoft 365: {str(e)}"
        )

# ----------------------------
# 📌 TRIGGER MANUAL SYNC (Background)
# ----------------------------
@router.post("/sync/trigger")
async def trigger_background_sync(
    background_tasks: BackgroundTasks,
    _auth=Depends(require_authentication)
):
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
        "last_sync": sync_scheduler.last_sync
    }

# ----------------------------
# 📌 GET SYNC STATUS
# ----------------------------
@router.get("/sync/status")
async def get_sync_status(
    _auth=Depends(require_authentication)
):
    """Get the status of the employee sync scheduler"""
    from core.background_tasks import sync_scheduler
    
    return {
        "is_running": sync_scheduler.is_running,
        "last_sync": sync_scheduler.last_sync,
        "sync_interval_hours": sync_scheduler.sync_interval_hours
    }
