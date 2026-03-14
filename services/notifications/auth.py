"""Authentication for Microsoft Graph API."""

from datetime import datetime, timedelta
from enum import StrEnum

import httpx

from core.config import settings


class GraphAuthScope(StrEnum):
    """Graph API authentication scopes."""

    GRAPH = "https://graph.microsoft.com/.default"


class GraphAuthClient:
    """Client for Microsoft Graph API authentication."""

    def __init__(self) -> None:
        self.tenant_id = settings.MICROSOFT_TENANT_ID or settings.TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID or settings.BACKEND_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET or settings.BACKEND_CLIENT_SECRET
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


async def get_graph_api_auth_headers(
    graph_scope: GraphAuthScope = GraphAuthScope.GRAPH,
) -> dict[str, str] | None:
    """Get authentication headers for Graph API."""
    return await graph_auth_client.get_auth_headers(graph_scope)
