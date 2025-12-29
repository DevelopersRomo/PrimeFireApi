"""Authentication for Microsoft Graph API."""

import httpx
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta
from core.config import settings


class GraphAuthScope(str, Enum):
    """Graph API authentication scopes."""

    GRAPH = "https://graph.microsoft.com/.default"


class GraphAuthClient:
    """Client for Microsoft Graph API authentication."""

    def __init__(self):
        self.tenant_id = settings.MICROSOFT_TENANT_ID or settings.TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID or settings.BACKEND_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET or settings.BACKEND_CLIENT_SECRET
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def get_access_token(
        self, graph_scope: GraphAuthScope = GraphAuthScope.GRAPH
    ) -> str:
        """Get access token using client credentials flow."""
        if (
            self._token
            and self._token_expiry
            and datetime.now() < self._token_expiry
        ):
            return self._token

        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )

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
            self._token_expiry = datetime.now() + timedelta(
                seconds=expires_in - 300
            )

            return self._token

    async def get_auth_headers(
        self, graph_scope: GraphAuthScope = GraphAuthScope.GRAPH
    ) -> Optional[dict[str, str]]:
        """Get authentication headers for Graph API."""
        try:
            access_token = await self.get_access_token(graph_scope)
            return {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        except Exception as e:
            print(f"Error getting auth headers: {e}")
            return None


graph_auth_client = GraphAuthClient()


async def get_graph_api_auth_headers(
    graph_scope: GraphAuthScope = GraphAuthScope.GRAPH,
) -> dict[str, str] | None:
    """Get authentication headers for Graph API."""
    return await graph_auth_client.get_auth_headers(graph_scope)

