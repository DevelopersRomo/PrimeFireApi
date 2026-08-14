"""Authentication for Microsoft Graph API."""

from datetime import datetime, timedelta
from enum import StrEnum

import httpx

from core.config import settings
from core.mail_profiles import DEFAULT_MAIL_PROFILE, get_mail_credentials, normalize_profile_key


class GraphAuthScope(StrEnum):
    """Graph API authentication scopes."""

    GRAPH = "https://graph.microsoft.com/.default"


class GraphAuthClient:
    """Client for Microsoft Graph API authentication."""

    def __init__(
        self,
        *,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self.tenant_id = tenant_id or settings.MICROSOFT_TENANT_ID or settings.TENANT_ID
        self.client_id = client_id or settings.MICROSOFT_CLIENT_ID or settings.BACKEND_CLIENT_ID
        self.client_secret = client_secret or settings.MICROSOFT_CLIENT_SECRET or settings.BACKEND_CLIENT_SECRET
        self._token: str | None = None
        self._token_expiry: datetime | None = None

    async def get_access_token(self, graph_scope: GraphAuthScope = GraphAuthScope.GRAPH) -> str:
        """Get access token using client credentials flow."""
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:  # noqa: DTZ005
            return self._token

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        payload = {
            "client_id": self.client_id,
            "scope": graph_scope.value,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(token_url, data=payload)
            response.raise_for_status()

            data = response.json()
            self._token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)  # noqa: DTZ005

            return self._token

    async def get_auth_headers(self, graph_scope: GraphAuthScope = GraphAuthScope.GRAPH) -> dict[str, str] | None:
        """Get authentication headers for Graph API."""
        try:
            access_token = await self.get_access_token(graph_scope)
            return {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        except Exception:
            return None


graph_auth_client = GraphAuthClient()

# One client per named mail profile, built on first use so each keeps its own token cache.
_profile_auth_clients: dict[str, GraphAuthClient] = {}


def get_auth_client(mail_profile: str = DEFAULT_MAIL_PROFILE) -> GraphAuthClient:
    """Get the auth client for a mail profile, or the default one when it is unconfigured."""
    credentials = get_mail_credentials(mail_profile)
    if not credentials:
        return graph_auth_client

    key = normalize_profile_key(mail_profile)
    if key not in _profile_auth_clients:
        _profile_auth_clients[key] = GraphAuthClient(
            tenant_id=credentials.tenant_id,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
        )
    return _profile_auth_clients[key]


async def get_graph_api_auth_headers(
    graph_scope: GraphAuthScope = GraphAuthScope.GRAPH,
    *,
    mail_profile: str = DEFAULT_MAIL_PROFILE,
) -> dict[str, str] | None:
    """Get authentication headers for Graph API, issued by the profile's tenant."""
    return await get_auth_client(mail_profile).get_auth_headers(graph_scope)
