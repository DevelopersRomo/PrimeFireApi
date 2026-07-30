import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import get_current_employee, require_module_permission
from bd.dependencies import get_main_db
from models.employees import Employees
from models.tenants import TenantEmployees, TenantLogos, Tenants
from schemas.pagination import PaginatedResponse
from schemas.tenants import (
    ApprovalRequest,
    TenantApprovalRequest,
    TenantCreate,
    TenantEmployeePendingRead,
    TenantLogoCreate,
    TenantLogoRead,
    TenantLogoUpdate,
    TenantRead,
    TenantUpdate,
)

router = APIRouter()


# ----------------------------
# 📌 DEBUG: LIST ALL TENANTS
# ----------------------------
@router.get("/list-all", response_model=list[TenantRead] | PaginatedResponse[TenantRead])
async def list_all_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_main_db),
):
    """List all tenants from MAIN database (for debugging/admin)."""
    tenants = list(
        db.exec(select(Tenants).order_by(Tenants.name, Tenants.tenant_id).offset(skip).limit(limit)).all()
    )
    if not with_meta:
        return tenants
    total = db.exec(select(func.count()).select_from(Tenants)).one()
    return PaginatedResponse[TenantRead](
        items=tenants,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(tenants) < total,
    )


# ----------------------------
# 📌 CREATE TENANT
# ----------------------------
@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_create")),
):
    """Create a new tenant."""
    tenant = Tenants(**tenant_data.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


# ----------------------------
# 📌 LIST MY TENANTS
# ----------------------------
@router.get("/my-tenants", response_model=list[TenantRead])
async def get_my_tenants(current_user: Employees = Depends(get_current_employee), db: Session = Depends(get_main_db)):
    """Get all tenants the current user has access to."""
    links = db.exec(select(TenantEmployees).where(TenantEmployees.email == current_user.email)).all()

    return [link.tenant for link in links if link.tenant and link.tenant.is_active]


# ----------------------------
# 📌 ADMIN: LIST PENDING USERS
# ----------------------------
@router.get(
    "/pending-users",
    response_model=list[TenantEmployeePendingRead] | PaginatedResponse[TenantEmployeePendingRead],
)
async def list_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_main_db),
):
    """List all external users pending tenant assignment (Admin only)."""
    # Users pending assignment (TenantId is NULL)
    filters = [TenantEmployees.tenant_id.is_(None)]
    external_users = db.exec(
        select(TenantEmployees)
        .where(*filters)
        .order_by(TenantEmployees.created_at.desc(), TenantEmployees.id.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    result = []
    for ext_user in external_users:
        tenant = db.get(Tenants, ext_user.tenant_id) if ext_user.tenant_id else None
        result.append(
            TenantEmployeePendingRead(
                id=ext_user.id,
                email=ext_user.email,
                tenant_id=ext_user.tenant_id,
                tenant_name=tenant.name if tenant else None,
                created_at=ext_user.created_at,
            )
        )
    if not with_meta:
        return result
    total = db.exec(select(func.count()).select_from(TenantEmployees).where(*filters)).one()
    return PaginatedResponse[TenantEmployeePendingRead](
        items=result,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(result) < total,
    )


# ----------------------------
# 📌 ADMIN: APPROVE USER AND ASSIGN TENANT
# ----------------------------
@router.post("/approve-user", response_model=dict)
async def approve_external_user(
    request: ApprovalRequest,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_edit")),
):
    """
    (Admin Only) Approve external user and assign tenant.
    Creates user in tenant's database and updates TenantEmployees record.
    """
    # 1. Get external user
    external_user = db.get(TenantEmployees, request.tenant_employee_id)
    if not external_user:
        raise HTTPException(status_code=404, detail="External user not found")

    # 2. Get tenant
    tenant = db.get(Tenants, request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.is_active:
        raise HTTPException(status_code=400, detail="Tenant is not active")

    # 3. Update pending user to point to the assigned tenant
    external_user.tenant_id = tenant.tenant_id
    db.add(external_user)
    db.commit()
    db.refresh(external_user)

    # 4. Create/Update user in MAIN database (ignoring tenant DB separation)
    # Check if user already exists in MAIN DB
    existing = db.exec(select(Employees).where(Employees.email == external_user.email)).first()

    if not existing:
        # Generate unique AzureOid for external users to avoid UNIQUE constraint violation
        external_oid = str(uuid.uuid4())
        new_employee = Employees(
            email=external_user.email,
            password_hash=external_user.password_hash,
            display_name=external_user.email.split("@")[0],  # Use email prefix as fallback
            title="External User",
            azure_oid=external_oid,  # Unique identifier for external users
        )
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
    else:
        # Update password if needed
        existing.password_hash = external_user.password_hash
        db.add(existing)
        db.commit()

    return {
        "message": "User approved and assigned to tenant",
        "tenant_employee_id": external_user.id,
        "tenant_id": tenant.tenant_id,
        "tenant_name": tenant.name,
        "status": "Active",
    }


# ----------------------------
# 📌 ADMIN: APPROVE TENANT (Legacy - for tenant management)
# ----------------------------
@router.post("/approve", response_model=TenantRead)
async def approve_tenant_request(
    request: TenantApprovalRequest,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_edit")),
):
    """(Admin Only) Approve a tenant request and assign connection key."""
    tenant = db.get(Tenants, request.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.is_active = True
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


# ----------------------------
# 📌 TENANT LOGOS CRUD
# ----------------------------
@router.post("/logos", response_model=TenantLogoRead, status_code=status.HTTP_201_CREATED)
async def create_tenant_logo(
    logo_data: TenantLogoCreate,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_create")),
):
    """Create a new logo for a tenant."""
    # Verify tenant exists
    tenant = db.get(Tenants, logo_data.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    logo = TenantLogos(**logo_data.model_dump())
    db.add(logo)
    db.commit()
    db.refresh(logo)
    return logo


@router.get("/logos", response_model=list[TenantLogoRead] | PaginatedResponse[TenantLogoRead])
async def list_tenant_logos(
    tenant_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_main_db),
):
    """List all logos, optionally filtered by tenant_id."""
    filters = []
    if tenant_id:
        filters.append(TenantLogos.tenant_id == tenant_id)

    query = select(TenantLogos)
    if filters:
        query = query.where(*filters)
    logos = list(
        db.exec(query.order_by(TenantLogos.title, TenantLogos.logo_id).offset(skip).limit(limit)).all()
    )
    if not with_meta:
        return logos
    count_query = select(func.count()).select_from(TenantLogos)
    if filters:
        count_query = count_query.where(*filters)
    total = db.exec(count_query).one()
    return PaginatedResponse[TenantLogoRead](
        items=logos,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(logos) < total,
    )


@router.get("/logos/{logo_id}", response_model=TenantLogoRead)
async def get_tenant_logo(logo_id: int, db: Session = Depends(get_main_db)):
    """Get a specific logo by ID."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")
    return logo


@router.get("/logos/by-url/{url}", response_model=TenantLogoRead)
async def get_tenant_logo_by_url(url: str, db: Session = Depends(get_main_db)):
    """
    Get logo configuration by URL identifier.
    This endpoint is public (no auth required) for frontend login page usage.
    """
    logo = db.exec(select(TenantLogos).where(TenantLogos.url == url)).first()
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found for the provided URL")
    return logo


@router.put("/logos/{logo_id}", response_model=TenantLogoRead)
@router.patch("/logos/{logo_id}", response_model=TenantLogoRead)
async def update_tenant_logo(
    logo_id: int,
    logo_data: TenantLogoUpdate,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_edit")),
):
    """Update a tenant logo."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")

    update_data = logo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(logo, field, value)

    logo.updated_at = datetime.now()  # noqa: DTZ005
    db.add(logo)
    db.commit()
    db.refresh(logo)
    return logo


@router.delete("/logos/{logo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant_logo(
    logo_id: int,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_delete")),
) -> None:
    """Delete a tenant logo."""
    logo = db.get(TenantLogos, logo_id)
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")

    db.delete(logo)
    db.commit()


# ----------------------------
# 📌 GET TENANT BY ID
# ----------------------------
@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    tenant_id: int, current_user: Employees = Depends(get_current_employee), db: Session = Depends(get_main_db)
):
    """Get a specific tenant by ID."""
    tenant = db.get(Tenants, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


# ----------------------------
# 📌 UPDATE TENANT
# ----------------------------
@router.put("/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_edit")),
):
    """Update an existing tenant."""
    tenant = db.get(Tenants, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

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
    db: Session = Depends(get_main_db),
    _permissions: dict = Depends(require_module_permission("tenants", "can_delete")),
) -> None:
    """Delete a tenant request. Only allowed if the tenant is in 'PENDING' state."""
    tenant = db.get(Tenants, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Only allow deleting inactive tenants
    if tenant.is_active:
        raise HTTPException(
            status_code=400, detail="Cannot delete active tenants. Only inactive tenants can be deleted."
        )

    # Cleanup associated employee links
    links = db.exec(select(TenantEmployees).where(TenantEmployees.tenant_id == tenant_id)).all()

    for link in links:
        db.delete(link)

    db.delete(tenant)
    db.commit()
