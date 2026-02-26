from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

# Import configuration
from api.dependencies import require_authentication
from core.config import AZURE_AUTH_SCHEME, settings
from models.employees import Employees

# Import routers with error handling
try:
    from api.licenses import router as licenses_router
    licenses_available = True
except Exception as e:
    print(f"Warning: Licenses router not available: {e}")
    licenses_available = False

try:
    from api.employees import router as employees_router
    employees_available = True
except Exception as e:
    print(f"Warning: Employees router not available: {e}")
    employees_available = False

try:
    from api.jobs import router as jobs_router
    jobs_available = True
except Exception as e:
    print(f"Warning: Jobs router not available: {e}")
    jobs_available = False

try:
    from api.curriculums import router as curriculums_router
    curriculums_available = True
except Exception as e:
    print(f"Warning: Curriculums router not available: {e}")
    curriculums_available = False

try:
    from api.roles import router as roles_router
    roles_available = True
except Exception as e:
    print(f"Warning: Roles router not available: {e}")
    roles_available = False

try:
    from api.countries import router as countries_router
    countries_available = True
except Exception as e:
    print(f"Warning: Countries router not available: {e}")
    countries_available = False

try:
    from api.modules import router as modules_router
    modules_available = True
except Exception as e:
    print(f"Warning: Modules router not available: {e}")
    modules_available = False

try:
    from api.permissions import router as permissions_router
    permissions_available = True
except Exception as e:
    print(f"Warning: Permissions router not available: {e}")
    permissions_available = False

try:
    from api.tickets import router as tickets_router
    tickets_available = True
except Exception as e:
    print(f"Warning: Tickets router not available: {e}")
    tickets_available = False

try:
    from api.ticket_messages import router as ticket_messages_router
    ticket_messages_available = True
except Exception as e:
    print(f"Warning: Ticket messages router not available: {e}")
    ticket_messages_available = False

try:
    from api.ticket_attachments import router as ticket_attachments_router
    ticket_attachments_available = True
except Exception as e:
    print(f"Warning: Ticket attachments router not available: {e}")
    ticket_attachments_available = False

try:
    from api.hardware_inventory import router as hardware_inventory_router
    hardware_inventory_available = True
except Exception as e:
    print(f"Warning: Hardware inventory router not available: {e}")
    hardware_inventory_available = False

try:
    from api.time_off import router as time_off_router
    time_off_available = True
except Exception as e:
    print(f"Warning: Time off router not available: {e}")
    time_off_available = False

try:
    from api.timesheet import router as timesheet_router
    timesheet_available = True
except Exception as e:
    print(f"Warning: Timesheet router not available: {e}")
    timesheet_available = False

try:
    from api.catalogs import router as catalogs_router
    catalogs_available = True
except Exception as e:
    print(f"Warning: Catalogs router not available: {e}")
    catalogs_available = False

try:
    from api.notifications import router as notifications_router
    notifications_available = True
except Exception as e:
    print(f"Warning: Notifications router not available: {e}")
    notifications_available = False

try:
    from api.tenants import router as tenants_router
    tenants_available = True
except Exception as e:
    print(f"Warning: Tenants router not available: {e}")
    tenants_available = False

try:
    from api.auth import router as auth_router
    auth_available = True
except Exception as e:
    print(f"Warning: Auth router not available: {e}")
    auth_available = False

try:
    from api.customers import router as customers_router
    customers_available = True
except Exception as e:
    print(f"Warning: Customers router not available: {e}")
    customers_available = False

try:
    from api.customer_notes import router as customer_notes_router
    customer_notes_available = True
except Exception as e:
    print(f"Warning: Customer notes router not available: {e}")
    customer_notes_available = False

try:
    from api.customer_contacts import router as customer_contacts_router
    customer_contacts_available = True
except Exception as e:
    print(f"Warning: Customer contacts router not available: {e}")
    customer_contacts_available = False

try:
    from api.customer_attachments import router as customer_attachments_router
    customer_attachments_available = True
except Exception as e:
    print(f"Warning: Customer attachments router not available: {e}")
    customer_attachments_available = False
    
try:
    from api.products import router as products_router
    products_available = True
except Exception as e:
    print(f"Warning: Products router not available: {e}")
    products_available = False


# Import database connection
try:
    from bd.connection import create_db_and_tables
    # Create tables
    create_db_and_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Database connection not available: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load OpenID Connect configuration and start background tasks on startup."""
    import asyncio
    
    # Load Azure AD configuration
    try:
        await AZURE_AUTH_SCHEME.openid_config.load_config()
        print("Azure AD configuration loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load Azure AD configuration: {e}")
    
    # Store background task reference for cleanup
    sync_task = None
    
    # Import and run sync scheduler in background
    if settings.SYNC_EMPLOYEES_PRIMEFIRE:
        try:
            from core.background_tasks import sync_scheduler
            
            # Run sync in background without blocking startup
            print("Starting initial employee sync from Microsoft 365 in background...")
            
            async def run_startup_sync():
                """Run sync in background task"""
                try:
                    await sync_scheduler.sync_on_startup()
                except asyncio.CancelledError:
                    # Task was cancelled during shutdown - this is normal
                    print("Startup sync task cancelled")
                    raise  # Re-raise to properly handle cancellation
                except Exception as e:
                    print(f"Warning: Background sync failed: {e}")
            
            # Create background task - doesn't block startup
            sync_task = asyncio.create_task(run_startup_sync())
            
            # OPTION 2: Start periodic sync (uncomment to enable continuous syncing)
            # await sync_scheduler.start_periodic_sync(interval_hours=settings.SYNC_INTERVAL_HOURS)
            
        except Exception as e:
            print(f"Warning: Could not start employee sync: {e}")
            print("   (API will continue running without automatic sync)")
    else:
        print("Auto-sync disabled (SYNC_EMPLOYEES_PRIMEFIRE=False)")
    
    yield
    
    # Cleanup on shutdown
    if sync_task:
        if not sync_task.done():
            sync_task.cancel()
            try:
                await asyncio.wait_for(sync_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                # Task was cancelled or timed out - this is expected during shutdown
                pass
            except Exception as e:
                # Log but don't fail shutdown
                print(f"Warning during sync task cleanup: {e}")
    
    try:
        from core.background_tasks import sync_scheduler
        await sync_scheduler.stop_periodic_sync()
    except Exception as e:
        # Don't fail shutdown if cleanup fails
        print(f"Warning during sync scheduler cleanup: {e}")

app = FastAPI(
    title="PrimeFire API",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.BACKEND_CLIENT_ID,
        "scopes": settings.scope_name,  # Solo solicita el scope de la API
    },
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 0,
    },
)

# Configure OAuth2 security scheme for Swagger UI
# This ensures that Swagger UI will show the OAuth2 login and pass tokens automatically
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="PrimeFire API",
        version="1.0.0",
        description="PrimeFire API with Azure AD authentication",
        routes=app.routes,
    )

    # Add OAuth2 security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "AzureAD_PKCE_single_tenant": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/authorize",
                    "tokenUrl": f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token",
                    "scopes": settings.scopes
                }
            }
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your token directly (from /auth/token or Azure AD)"
        }
    }

    # Apply security globally - Swagger UI will automatically include tokens for these endpoints
    openapi_schema["security"] = [
        {"AzureAD_PKCE_single_tenant": list(settings.scopes.keys())},
        {"BearerAuth": []}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

origins = [
    "https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net",
    "https://app.devromo.com",
    "https://app.primefire.us",
    "http://localhost:4200",
    "http://localhost:4201",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers conditionally
if licenses_available:
    app.include_router(licenses_router, prefix="/licenses", tags=["licenses"])
    
if employees_available:
    app.include_router(employees_router, prefix="/employees", tags=["employees"])
    
if jobs_available:
    app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
    
if curriculums_available:
    app.include_router(curriculums_router, prefix="/curriculums", tags=["curriculums"])

if roles_available:
    app.include_router(roles_router, prefix="/roles", tags=["roles"])

if countries_available:
    app.include_router(countries_router, prefix="/countries", tags=["countries"])

if modules_available:
    app.include_router(modules_router, prefix="/modules", tags=["modules"])

if permissions_available:
    app.include_router(permissions_router, prefix="/permissions", tags=["permissions"])

if tickets_available:
    app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
    
if hardware_inventory_available:
    app.include_router(hardware_inventory_router, prefix="/hardware", tags=["hardware_inventory"])

if ticket_messages_available:
    # messages endpoints live under both /tickets/{ticket_id}/messages and /messages
    app.include_router(ticket_messages_router, tags=["ticket_messages"])

if ticket_attachments_available:
    app.include_router(ticket_attachments_router, tags=["ticket_attachments"])

if time_off_available:
    app.include_router(time_off_router, tags=["time_off"])

if timesheet_available:
    app.include_router(timesheet_router, tags=["timesheet"])

if catalogs_available:
    app.include_router(catalogs_router, tags=["catalogs"])

if notifications_available:
    app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
if tenants_available:
    app.include_router(tenants_router, prefix="/tenants", tags=["tenants"])

if auth_available:
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])

if customers_available:
    app.include_router(customers_router, prefix="/customers", tags=["customers"])

if customer_notes_available:
    app.include_router(customer_notes_router, tags=["customer_notes"])

if customer_contacts_available:
    app.include_router(customer_contacts_router, tags=["customer_contacts"])

if customer_attachments_available:
    app.include_router(customer_attachments_router, tags=["customer_attachments"])
if products_available:
    app.include_router(products_router, prefix="/products", tags=["products"])


@app.get("/")
async def root():
    """Root endpoint. Redirects to docs."""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/debug-auth")
async def debug_auth(current_user=Depends(AZURE_AUTH_SCHEME)):
    """Debug authentication endpoint."""
    return {
        "message": "Authentication successful!",
        "user_info": {
            "name": getattr(current_user, 'name', 'N/A'),
            "email": getattr(current_user, 'preferred_username', 'N/A'),
            "oid": getattr(current_user, 'oid', 'N/A'),
        }
    }

@app.get("/debug-token")
async def debug_token(current_user: Employees = Depends(require_authentication)):
    """Debug token endpoint using our custom validator."""
    return {
        "message": "Token validation successful!",
        "user": {
            "id": current_user.EmployeeId,
            "name": current_user.Name,
            "email": current_user.Email,
            "title": current_user.Title,
            "azure_oid": current_user.AzureOid,
            "role_id": current_user.RoleId
        }
    }
