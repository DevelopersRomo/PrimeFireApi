from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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
    from api.hardware_inventory import router as licenses_router
    hardware_inventory_available = True
except Exception as e:
    print(f"Warning: Hardware inventory router not available: {e}")
    hardware_inventory_available = False

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
    # Load Azure AD configuration
    try:
        await AZURE_AUTH_SCHEME.openid_config.load_config()
        print("Azure AD configuration loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load Azure AD configuration: {e}")
    
    # Import and run sync scheduler
    if settings.ENABLE_AUTO_SYNC:
        try:
            from core.background_tasks import sync_scheduler
            
            # OPTION 1: Sync only on startup (recommended)
            print("🔄 Running initial employee sync from Microsoft 365...")
            await sync_scheduler.sync_on_startup()
            
            # OPTION 2: Start periodic sync (uncomment to enable continuous syncing)
            # await sync_scheduler.start_periodic_sync(interval_hours=settings.SYNC_INTERVAL_HOURS)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not run employee sync: {e}")
            print("   (API will continue running without automatic sync)")
    else:
        print("ℹ️ Auto-sync disabled (ENABLE_AUTO_SYNC=False)")
    
    yield
    
    # Cleanup on shutdown
    try:
        from core.background_tasks import sync_scheduler
        await sync_scheduler.stop_periodic_sync()
    except:
        pass

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
        }
    }

    # Apply security globally - Swagger UI will automatically include tokens for these endpoints
    openapi_schema["security"] = [{"AzureAD_PKCE_single_tenant": list(settings.scopes.keys())}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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

if ticket_messages_available:
    # messages endpoints live under both /tickets/{ticket_id}/messages and /messages
    app.include_router(ticket_messages_router, tags=["ticket_messages"])

if ticket_attachments_available:
    app.include_router(ticket_attachments_router, tags=["ticket_attachments"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PrimeFire API is running!"}

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
