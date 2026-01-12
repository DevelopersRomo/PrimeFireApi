from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid

from bd.dependencies import get_db, get_main_db
from api.dependencies import require_authentication, get_current_employee
from models.employees import Employees
from models.tenants import Tenants, TenantEmployees, TenantLogos
from schemas.tenants import TenantCreate, TenantRead, TenantEmployeeRegister, TenantEmployeeRead, ApprovalRequest, TenantApprovalRequest, ExternalUserRead, TenantLogoCreate, TenantLogoUpdate, TenantLogoRead
from models.external_users import ExternalUsers
from bd.multitenancy import ConnectionManager

router = APIRouter()

# ----------------------------
# 📌 DEBUG: LIST ALL TENANTS
# ----------------------------
@router.get("/list-all", response_model=List[TenantRead])
async def list_all_tenants():
    """List all tenants from MAIN database (for debugging/admin)."""
    from bd.connection import SessionLocal
    db = SessionLocal()
    try:
        tenants = db.exec(select(Tenants)).all()
        return list(tenants) if tenants else []
    finally:
        db.close()

# ----------------------------
# 📌 TENANT REGISTRATION (User requests access)
# ----------------------------
@router.post("/register-access", response_model=TenantEmployeeRead)
async def register_user_tenant_access(
    registration_data: TenantEmployeeRegister,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db) 
):
    """
    Solicitar acceso a un Tenant.
    El usuario ya debe estar registrado y logueado.
    """
    # 1. Update User Profile if needed
    if registration_data.FirstName: current_user.FirstName = registration_data.FirstName
    if registration_data.LastName: current_user.LastName = registration_data.LastName
    if registration_data.Phone: current_user.Phone = registration_data.Phone
    
    db.add(current_user)
    
    # 2. Check existing request
    existing_request = db.exec(
        select(TenantEmployees).where(TenantEmployees.EmployeeId == current_user.EmployeeId)
    ).first()
    
    if existing_request:
        tenant_name = existing_request.tenant.Name if existing_request.tenant else "Unknown"
        return TenantEmployeeRead(
            Id=existing_request.Id,
            TenantId=existing_request.TenantId,
            EmployeeId=existing_request.EmployeeId,
            Status=existing_request.Status,
            IsDefault=existing_request.IsDefault,
            TenantName=tenant_name
        )

    # 3. Find or Create Tenant Placeholder
    tenant = db.exec(select(Tenants).where(Tenants.Name == registration_data.CompanyName)).first()
    
    if not tenant:
        tenant = Tenants(
            Name=registration_data.CompanyName,
            DbConnectionKey="PENDING", 
            IsActive=False,
            Description="Created via user registration"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    # 4. Create Link
    link = TenantEmployees(
        TenantId=tenant.TenantId,
        EmployeeId=current_user.EmployeeId,
        Status="Pending",
        IsDefault=True
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    
    return TenantEmployeeRead(
        Id=link.Id,
        TenantId=link.TenantId,
        EmployeeId=link.EmployeeId,
        Status=link.Status,
        IsDefault=link.IsDefault,
        TenantName=tenant.Name
    )

# ----------------------------
# 📌 LIST MY TENANTS
# ----------------------------
@router.get("/my-tenants", response_model=List[TenantRead])
async def get_my_tenants(
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    """Get all tenants the current user has access to."""
    links = db.exec(
        select(TenantEmployees).where(TenantEmployees.EmployeeId == current_user.EmployeeId)
    ).all()
    
    tenants = []
    for link in links:
         if link.tenant and link.tenant.IsActive:
             tenants.append(link.tenant)
             
    return tenants

# ----------------------------
# 📌 ADMIN: LIST PENDING USERS
# ----------------------------
@router.get("/pending-users", response_model=List[ExternalUserRead])
async def list_pending_users():
    """List all external users pending tenant assignment (Admin only)."""
    from bd.connection import SessionLocal
    db = SessionLocal()
    try:
        # Get users with PENDING tenant or no tenant assigned
        pending_tenant = db.exec(
            select(Tenants).where(Tenants.DbConnectionKey == "PENDING")
        ).first()
        
        if not pending_tenant:
            return []
        
        external_users = db.exec(
            select(ExternalUsers).where(ExternalUsers.TenantId == pending_tenant.TenantId)
        ).all()
        
        result = []
        for ext_user in external_users:
            tenant = db.get(Tenants, ext_user.TenantId)
            result.append(ExternalUserRead(
                ExternalUserId=ext_user.ExternalUserId,
                Email=ext_user.Email,
                TenantId=ext_user.TenantId,
                TenantName=tenant.Name if tenant else None,
                CreatedAt=ext_user.CreatedAt
            ))
        return result
    finally:
        db.close()

# ----------------------------
# 📌 ADMIN: APPROVE USER AND ASSIGN TENANT
# ----------------------------
@router.post("/approve-user", response_model=dict)
async def approve_external_user(
    request: ApprovalRequest,
    current_user: Employees = Depends(get_current_employee),
):
    """
    (Admin Only) Approve external user and assign tenant.
    Creates user in tenant's database and updates ExternalUsers record.
    """
    from bd.connection import SessionLocal
    db = SessionLocal()
    try:
        # 1. Get external user
        external_user = db.get(ExternalUsers, request.ExternalUserId)
        if not external_user:
            raise HTTPException(status_code=404, detail="External user not found")
        
        # 2. Get tenant
        tenant = db.get(Tenants, request.TenantId)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        if not tenant.IsActive:
            raise HTTPException(status_code=400, detail="Tenant is not active")
        
        # 3. Update ExternalUsers to point to the assigned tenant
        external_user.TenantId = tenant.TenantId
        db.add(external_user)
        db.commit()
        db.refresh(external_user)
        
        # 4. Create user in tenant's database
        tenant_db = ConnectionManager.get_session(tenant.DbConnectionKey)
        try:
            # Check if user already exists in tenant DB
            existing = tenant_db.exec(
                select(Employees).where(Employees.Email == external_user.Email)
            ).first()
            
            if not existing:
                # Get user info from ExternalUsers (we need to store it somewhere or get it from registration)
                # For now, create minimal user - admin can update later
                # Generate unique AzureOid for external users to avoid UNIQUE constraint violation
                external_oid = str(uuid.uuid4())
                new_employee = Employees(
                    Email=external_user.Email,
                    PasswordHash=external_user.PasswordHash,
                    DisplayName=external_user.Email.split('@')[0],  # Use email prefix as fallback
                    Title="External User",
                    AzureOid=external_oid  # Unique identifier for external users
                )
                tenant_db.add(new_employee)
                tenant_db.commit()
                tenant_db.refresh(new_employee)
            else:
                # Update password if needed
                existing.PasswordHash = external_user.PasswordHash
                tenant_db.add(existing)
                tenant_db.commit()
        finally:
            tenant_db.close()
        
        return {
            "message": "User approved and assigned to tenant",
            "external_user_id": external_user.ExternalUserId,
            "tenant_id": tenant.TenantId,
            "tenant_name": tenant.Name,
            "status": request.Status
        }
    finally:
        db.close()

# ----------------------------
# 📌 ADMIN: APPROVE TENANT (Legacy - for tenant management)
# ----------------------------
@router.post("/approve", response_model=TenantRead)
async def approve_tenant_request(
    request: TenantApprovalRequest,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    """
    (Admin Only) Approve a tenant request and assign connection key.
    """
    tenant = db.get(Tenants, request.TenantId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant.IsActive = True
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

# ----------------------------
# 📌 ADMIN: DELETE PENDING TENANT
# ----------------------------
@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant_request(
    tenant_id: int,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    """
    Delete a tenant request. Only allowed if the tenant is in 'PENDING' state.
    """
    tenant = db.get(Tenants, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Only allow deleting PENDING tenants
    if tenant.DbConnectionKey != "PENDING":
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete active tenants. Only PENDING tenants can be deleted."
        )
    
    # Cleanup associated employee links
    links = db.exec(
        select(TenantEmployees).where(TenantEmployees.TenantId == tenant_id)
    ).all()
    
    for link in links:
        db.delete(link)
        
    db.delete(tenant)
    db.commit()
    return None

# ----------------------------
# 📌 TENANT LOGOS CRUD
# ----------------------------
@router.post("/logos", response_model=TenantLogoRead, status_code=status.HTTP_201_CREATED)
async def create_tenant_logo(
    logo_data: TenantLogoCreate,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_main_db)
):
    """Create a new logo for a tenant."""
    # Verify tenant exists
    tenant = db.get(Tenants, logo_data.TenantId)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    logo = TenantLogos(**logo_data.model_dump())
    db.add(logo)
    db.commit()
    db.refresh(logo)
    return logo

@router.get("/logos", response_model=List[TenantLogoRead])
async def list_tenant_logos(
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_main_db)
):
    """List all logos, optionally filtered by tenant_id."""
    query = select(TenantLogos)
    if tenant_id:
        query = query.where(TenantLogos.TenantId == tenant_id)
    
    logos = db.exec(query).all()
    return list(logos) if logos else []

@router.get("/logos/{logo_id}", response_model=TenantLogoRead)
async def get_tenant_logo(
    logo_id: int,
    db: Session = Depends(get_main_db)
):
    """Get a specific logo by ID."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")
    return logo

@router.get("/logos/by-url/{url}", response_model=TenantLogoRead)
async def get_tenant_logo_by_url(
    url: str,
    db: Session = Depends(get_main_db)
):
    """
    Get logo configuration by URL identifier.
    This endpoint is public (no auth required) for frontend login page usage.
    """
    logo = db.exec(select(TenantLogos).where(TenantLogos.Url == url)).first()
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found for the provided URL")
    return logo

@router.put("/logos/{logo_id}", response_model=TenantLogoRead)
async def update_tenant_logo(
    logo_id: int,
    logo_data: TenantLogoUpdate,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_main_db)
):
    """Update a tenant logo."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    update_data = logo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(logo, field, value)
    
    logo.UpdatedAt = datetime.now()
    db.add(logo)
    db.commit()
    db.refresh(logo)
    return logo

@router.delete("/logos/{logo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant_logo(
    logo_id: int,
    current_user: Employees = Depends(get_current_employee),
    db: Session = Depends(get_main_db)
):
    """Delete a tenant logo."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")
    
    db.delete(logo)
    db.commit()
    return None
