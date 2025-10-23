"""Configuration."""

from enum import Enum

from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentMode(str, Enum):
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
    ]

    # Azure AD Authentication
    TENANT_ID: str = Field(
        default="",
        validation_alias="TENANT_ID",
        description="Azure AD Tenant ID"
    )
    BACKEND_CLIENT_ID: str = Field(
        default="",
        validation_alias="BACKEND_CLIENT_ID",
        description="Azure AD Application (client) ID for backend"
    )
    BACKEND_CLIENT_SECRET: str = Field(
        default="",
        validation_alias="BACKEND_CLIENT_SECRET",
        description="Azure AD Client Secret for backend"
    )
    FRONTEND_CLIENT_ID: str = Field(
        default="",
        validation_alias="FRONTEND_CLIENT_ID",
        description="Azure AD Application (client) ID for frontend"
    )

    SCOPE_DESCRIPTION: str = "user_impersonation"

    # Microsoft Graph API credentials (for service-to-service)
    MICROSOFT_TENANT_ID: str = Field(
        default="",
        validation_alias="MICROSOFT_TENANT_ID",
        description="Microsoft tenant ID for Graph API"
    )
    MICROSOFT_CLIENT_ID: str = Field(
        default="",
        validation_alias="MICROSOFT_CLIENT_ID",
        description="Microsoft client ID for Graph API"
    )
    MICROSOFT_CLIENT_SECRET: str = Field(
        default="",
        validation_alias="MICROSOFT_CLIENT_SECRET",
        description="Microsoft client secret for Graph API"
    )
    
    # Employee sync settings
    ENABLE_AUTO_SYNC: bool = Field(
        default=True,
        validation_alias="ENABLE_AUTO_SYNC",
        description="Enable automatic employee sync on startup"
    )
    SYNC_INTERVAL_HOURS: int = Field(
        default=24,
        validation_alias="SYNC_INTERVAL_HOURS",
        description="Hours between automatic syncs (if periodic sync enabled)"
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

