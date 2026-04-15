"""Configuration."""

from enum import StrEnum

from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentMode(StrEnum):
    """Environment type."""

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    APP_NAME: str = "PrimeFire"
    SWAGGER_PASSWORD: str = "admin"
    SWAGGER_USERNAME: str = "admin"

    @property
    def app_name_lowered(self) -> str:
        """Returns the lowercase version of the app name."""
        return self.APP_NAME.lower().replace(" ", "").replace("-", "").lower()

    ENVIRONMENT: EnvironmentMode = Field(
        default=EnvironmentMode.LOCAL,
        validation_alias="ENVIRONMENT",
    )
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:4201",
    ]

    # Azure AD Authentication
    TENANT_ID: str = Field(default="", validation_alias="TENANT_ID", description="Azure AD Tenant ID")
    BACKEND_CLIENT_ID: str = Field(
        default="", validation_alias="BACKEND_CLIENT_ID", description="Azure AD Application (client) ID for backend"
    )
    BACKEND_CLIENT_SECRET: str = Field(
        default="", validation_alias="BACKEND_CLIENT_SECRET", description="Azure AD Client Secret for backend"
    )
    FRONTEND_CLIENT_ID: str = Field(
        default="", validation_alias="FRONTEND_CLIENT_ID", description="Azure AD Application (client) ID for frontend"
    )

    SCOPE_DESCRIPTION: str = "user_impersonation"

    # Microsoft Graph API credentials (for service-to-service)
    MICROSOFT_TENANT_ID: str = Field(
        default="", validation_alias="MICROSOFT_TENANT_ID", description="Microsoft tenant ID for Graph API"
    )
    MICROSOFT_CLIENT_ID: str = Field(
        default="", validation_alias="MICROSOFT_CLIENT_ID", description="Microsoft client ID for Graph API"
    )
    MICROSOFT_CLIENT_SECRET: str = Field(
        default="", validation_alias="MICROSOFT_CLIENT_SECRET", description="Microsoft client secret for Graph API"
    )

    # Employee sync settings
    SYNC_EMPLOYEES_PRIMEFIRE: bool = Field(
        default=True,
        validation_alias="SYNC_EMPLOYEES_PRIMEFIRE",
        description="Enable initial employee sync from Microsoft 365 in background",
    )
    ENABLE_AUTO_SYNC: bool = Field(
        default=True,
        validation_alias="ENABLE_AUTO_SYNC",
        description="Enable automatic employee sync on startup (Legacy)",
    )
    SYNC_INTERVAL_HOURS: int = Field(
        default=24,
        validation_alias="SYNC_INTERVAL_HOURS",
        description="Hours between automatic syncs (if periodic sync enabled)",
    )

    # Notification settings
    SEND_NOTIFICATIONS: bool = Field(
        default=True,
        validation_alias="SEND_NOTIFICATIONS",
        description="Enable/disable all notifications (default: True for production)",
    )
    BOT_EMAIL: str = Field(
        default="", validation_alias="BOT_EMAIL", description="Email address for bot to send notifications"
    )
    SUPPORT_EMAIL: str = Field(
        default="info@primefire.us",
        validation_alias="SUPPORT_EMAIL",
        description="Support email address for notifications",
    )
    APP_URL: str = Field(
        default="https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net",
        validation_alias="APP_URL",
        description="Application URL for notification links",
    )
    CONTACT_PRIMEFIRE_API_TOKEN: str = Field(
        default="7dd8430e-2c2b-4239-9ddf-b299dea05bc4",
        validation_alias="CONTACT_PRIMEFIRE_API_TOKEN",
        description="Static API token for /notifications/send/contact-primefire endpoint",
    )
    CLOUDFLARE_TURNSTILE_SECRET_KEY: str = Field(
        default="",
        validation_alias="CLOUDFLARE_TURNSTILE_SECRET_KEY",
        description="Cloudflare Turnstile secret key used to validate contact form captcha tokens",
    )
    CLOUDFLARE_TURNSTILE_ALLOWED_HOSTNAMES: str = Field(
        default="primefire.us,www.primefire.us,primefire.do,www.primefire.do",
        validation_alias="CLOUDFLARE_TURNSTILE_ALLOWED_HOSTNAMES",
        description="Comma-separated hostnames allowed in Cloudflare Turnstile verification results",
    )
    CONTACT_PRIMEFIRE_RATE_LIMIT_MAX_REQUESTS: int = Field(
        default=3,
        validation_alias="CONTACT_PRIMEFIRE_RATE_LIMIT_MAX_REQUESTS",
        description="Maximum contact submissions allowed per IP in the configured rate limit window",
    )
    CONTACT_PRIMEFIRE_RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=600,
        validation_alias="CONTACT_PRIMEFIRE_RATE_LIMIT_WINDOW_SECONDS",
        description="Rate limit window for contact submissions, in seconds",
    )
    CONTACT_PRIMEFIRE_DUPLICATE_WINDOW_SECONDS: int = Field(
        default=600,
        validation_alias="CONTACT_PRIMEFIRE_DUPLICATE_WINDOW_SECONDS",
        description="Window used to block duplicate contact submissions, in seconds",
    )

    # File upload settings
    UPLOAD_DIR: str = Field(
        default="uploads",
        validation_alias="UPLOAD_DIR",
        description="Directory for uploaded files (use /home/uploads in Azure Linux)",
    )

    # IP Geolocation
    IPGEOLOCATION_API_KEY: str = Field(
        default="", validation_alias="IPGEOLOCATION_API_KEY", description="API key for ipgeolocation.io"
    )

    # Ticket Recurrence Scheduler
    RECURRENCE_JOB_INTERVAL_HOURS: int = Field(
        default=1,
        validation_alias="RECURRENCE_JOB_INTERVAL_HOURS",
        description="Hours between ticket recurrence job runs (default: 1)",
    )

    @property
    def scope_name(self) -> str:
        """Returns the scope name."""
        return f"api://{self.BACKEND_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @property
    def scopes(self) -> dict:
        """Returns the scopes."""
        return {
            self.scope_name: self.SCOPE_DESCRIPTION,
            "profile": "profile",
        }


settings = Settings()

AZURE_AUTH_SCHEME = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=f"api://{settings.BACKEND_CLIENT_ID}",  # Match the audience in the token
    tenant_id=settings.TENANT_ID,
    scopes=settings.scopes,
    leeway=60,  # Add 60 seconds leeway for token validation
    allow_guest_users=True,  # Allow guest users temporarily for debugging
)
