from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api.auth import router as auth_router
from api.backups import router as backups_router
from api.catalogs import router as catalogs_router
from api.countries import router as countries_router
from api.curriculums import router as curriculums_router
from api.customer_attachments import router as customer_attachments_router
from api.customer_contacts import router as customer_contacts_router
from api.customer_notes import router as customer_notes_router
from api.customers import router as customers_router

# Config
from api.dependencies import require_authentication
from api.employees import router as employees_router
from api.hardware_inventory import router as hardware_inventory_router
from api.jobs import router as jobs_router

# Routers
from api.licenses import router as licenses_router
from api.modules import router as modules_router
from api.notifications import router as notifications_router
from api.permissions import router as permissions_router
from api.products import router as products_router
from api.quotations import router as quotations_router
from api.roles import router as roles_router
from api.tenants import router as tenants_router
from api.ticket_attachments import router as ticket_attachments_router
from api.ticket_messages import router as ticket_messages_router
from api.tickets import router as tickets_router
from api.time_off import router as time_off_router
from api.timesheet import router as timesheet_router

# DB
from bd.connection import create_db_and_tables
from core.config import AZURE_AUTH_SCHEME, settings
from models.employees import Employees

create_db_and_tables()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    with suppress(Exception):
        await AZURE_AUTH_SCHEME.openid_config.load_config()

    sync_task = None

    if settings.SYNC_EMPLOYEES_PRIMEFIRE:
        try:
            from core.background_tasks import sync_scheduler

            async def run_startup_sync() -> None:
                try:
                    await sync_scheduler.sync_on_startup()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

            sync_task = asyncio.create_task(run_startup_sync())

        except Exception:
            pass

    # Start ticket recurrence scheduler
    recurrence_task = None
    try:
        from core.ticket_recurrence_scheduler import recurrence_scheduler

        recurrence_task = asyncio.create_task(
            recurrence_scheduler.start(interval_seconds=settings.RECURRENCE_JOB_INTERVAL_HOURS * 3600)
        )
    except Exception:
        pass

    yield

    if sync_task and not sync_task.done():
        sync_task.cancel()

    try:
        from core.background_tasks import sync_scheduler

        await sync_scheduler.stop_periodic_sync()
    except Exception:
        pass

    if recurrence_task and not recurrence_task.done():
        recurrence_task.cancel()
        with suppress(asyncio.CancelledError):
            await recurrence_task

    try:
        from core.ticket_recurrence_scheduler import recurrence_scheduler

        await recurrence_scheduler.stop()
    except Exception:
        pass


app = FastAPI(
    title="PrimeFire API",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.BACKEND_CLIENT_ID,
        "scopes": settings.scope_name,
    },
    swagger_ui_parameters={
        "docExpansion": "none",
        "persistAuthorization": True,
    },
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="PrimeFire API",
        version="1.0.0",
        description="PrimeFire API with Azure AD authentication",
        routes=app.routes,
    )

    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})

    # Preserve existing schemes and expose both Azure PKCE and local token auth.
    security_schemes.update(
        {
            "AzureAD_PKCE_single_tenant": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/authorize",
                        "tokenUrl": f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token",
                        "scopes": settings.scopes,
                    }
                },
            },
            "LocalPasswordAuth": {"type": "oauth2", "flows": {"password": {"tokenUrl": "/auth/token", "scopes": {}}}},
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "ContactTokenAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "x-contact-token",
                "description": "Static token for /notifications/send/contact-primefire",
            },
        }
    )

    openapi_schema["security"] = [
        {"AzureAD_PKCE_single_tenant": list(settings.scopes.keys())},
        {"LocalPasswordAuth": []},
        {"BearerAuth": []},
    ]

    contact_path = openapi_schema.get("paths", {}).get(
        "/notifications/send/contact-primefire",
        {},
    )
    contact_post = contact_path.get("post")
    if contact_post:
        contact_post["security"] = [{"ContactTokenAuth": []}]

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom CORS middleware for open endpoints like contact-primefire
class OpenCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        open_paths = {
            "/notifications/send/contact-primefire",
            "/notifications/send/contact-primefire/",
        }

        if request.url.path in open_paths:
            if request.method == "OPTIONS":
                # Handle preflight here so this endpoint is CORS-open regardless of global origins.
                return Response(
                    status_code=204,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": request.headers.get(
                            "access-control-request-headers",
                            "*",
                        ),
                        "Access-Control-Max-Age": "86400",
                    },
                )

            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = request.headers.get(
                "access-control-request-headers",
                "*",
            )
            return response
        return await call_next(request)


app.add_middleware(OpenCORSMiddleware)


# Routers
app.include_router(licenses_router, prefix="/licenses", tags=["licenses"])
app.include_router(employees_router, prefix="/employees", tags=["employees"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(curriculums_router, prefix="/curriculums", tags=["curriculums"])
app.include_router(roles_router, prefix="/roles", tags=["roles"])
app.include_router(countries_router, prefix="/countries", tags=["countries"])
app.include_router(modules_router, prefix="/modules", tags=["modules"])
app.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
app.include_router(ticket_messages_router, tags=["ticket_messages"])
app.include_router(ticket_attachments_router, tags=["ticket_attachments"])
app.include_router(hardware_inventory_router, prefix="/hardware", tags=["hardware"])
app.include_router(time_off_router, tags=["time_off"])
app.include_router(timesheet_router, tags=["timesheet"])
app.include_router(catalogs_router, tags=["catalogs"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(customers_router, prefix="/customers", tags=["customers"])
app.include_router(customer_notes_router, tags=["customer_notes"])
app.include_router(customer_contacts_router, tags=["customer_contacts"])
app.include_router(customer_attachments_router, tags=["customer_attachments"])

# IMPORTANT
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(quotations_router)  # prefix already defined in router
app.include_router(backups_router, prefix="/backups", tags=["backups"])


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/debug-auth")
async def debug_auth(current_user=Depends(AZURE_AUTH_SCHEME)):
    return {
        "message": "Authentication successful!",
        "user_info": {
            "name": getattr(current_user, "name", "N/A"),
            "email": getattr(current_user, "preferred_username", "N/A"),
            "oid": getattr(current_user, "oid", "N/A"),
        },
    }


@app.get("/debug-token")
async def debug_token(current_user: Employees = Depends(require_authentication)):
    return {
        "message": "Token validation successful!",
        "user": {
            "id": current_user.employee_id,
            "name": current_user.display_name,
            "email": current_user.email,
            "title": current_user.title,
            "azure_oid": current_user.azure_oid,
        },
    }
