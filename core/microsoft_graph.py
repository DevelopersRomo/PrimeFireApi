import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0  # seconds, doubles each retry


class MicrosoftGraphClient:
    """
    Client for Microsoft Graph API to manage users.
    Includes retry logic for transient failures (rate limits, 5xx, network errors).
    """

    def __init__(self) -> None:
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self._token: str | None = None
        self._token_expiry: datetime | None = None
        self._token_lock = asyncio.Lock()

    async def _get_access_token(self) -> str:
        """Get access token using client credentials flow (thread-safe via lock)."""
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:  # noqa: DTZ005
            return self._token

        async with self._token_lock:
            # Double-check after acquiring lock
            if self._token and self._token_expiry and datetime.now() < self._token_expiry:  # noqa: DTZ005
                return self._token

            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "https://graph.microsoft.com/.default",
                        "grant_type": "client_credentials",
                    },
                )
                response.raise_for_status()

                data = response.json()
                self._token = data["access_token"]
                self._token_expiry = datetime.now() + timedelta(  # noqa: DTZ005
                    seconds=data.get("expires_in", 3600) - 300
                )

                return self._token

    def _invalidate_token(self) -> None:
        """Force token refresh on next request (call on 401)."""
        self._token = None
        self._token_expiry = None

    async def _make_request(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make authenticated request to Graph API with retry logic."""
        last_exception: Exception | None = None
        token_refreshed = False

        for attempt in range(MAX_RETRIES + 1):
            try:
                token = await self._get_access_token()
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                url = f"{self.graph_url}{endpoint}"

                async with httpx.AsyncClient() as client:
                    if method == "GET":
                        response = await client.get(url, headers=headers)
                    elif method == "PATCH":
                        response = await client.patch(url, headers=headers, json=data)
                    elif method == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    elif method == "PUT":
                        response = await client.put(url, headers=headers, json=data)
                    elif method == "DELETE":
                        response = await client.delete(url, headers=headers)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                # 401/403 → token may be stale or missing recently-granted permissions
                if response.status_code in (401, 403) and not token_refreshed:
                    self._invalidate_token()
                    token_refreshed = True
                    continue

                # Rate limit or server error → retry with backoff
                if response.status_code in RETRYABLE_STATUSES and attempt < MAX_RETRIES:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        wait = float(retry_after)
                    else:
                        wait = RETRY_BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "Graph API %s %s → %d, retrying in %.1fs (attempt %d/%d)",
                        method,
                        endpoint,
                        response.status_code,
                        wait,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    await asyncio.sleep(wait)
                    continue

                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError:
                    # Log the full Graph API error body before re-raising
                    try:
                        error_body = response.text
                    except Exception:
                        error_body = "<unable to read response body>"
                    logger.error(
                        "Graph API %s %s → %d\nRequest body: %s\nResponse: %s",
                        method,
                        endpoint,
                        response.status_code,
                        data,
                        error_body,
                    )
                    raise

                if response.status_code == 204:
                    return {}

                return response.json()

            except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_exception = e
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF_BASE * (2**attempt)
                    logger.warning(
                        "Graph API network error on %s %s: %s, retrying in %.1fs (attempt %d/%d)",
                        method,
                        endpoint,
                        e,
                        wait,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    await asyncio.sleep(wait)
                continue

            except httpx.HTTPStatusError as e:
                # Non-retryable HTTP error (4xx except 401/429) → fail immediately
                raise

        # All retries exhausted
        raise last_exception or RuntimeError(
            f"Graph API {method} {endpoint} failed after {MAX_RETRIES} retries"
        )

    async def get_all_users(self) -> list[dict[str, Any]]:
        """Get all users from Microsoft 365."""
        users = []
        endpoint = "/users?$select=id,userPrincipalName,displayName,givenName,surname,jobTitle,department,officeLocation,mail,businessPhones,mobilePhone,streetAddress,city,state,postalCode,country,countryLetterCode&$expand=manager($select=displayName,mail,userPrincipalName)"

        while endpoint:
            data = await self._make_request("GET", endpoint)
            users.extend(data.get("value", []))
            endpoint = data.get("@odata.nextLink", "").replace(self.graph_url, "")

        return users

    async def get_user(self, user_id: str) -> dict[str, Any]:
        """Get a single user by ID or userPrincipalName."""
        endpoint = f"/users/{user_id}?$select=id,userPrincipalName,displayName,givenName,surname,jobTitle,department,officeLocation,mail,businessPhones,mobilePhone,streetAddress,city,state,postalCode,country,countryLetterCode&$expand=manager($select=displayName,mail,userPrincipalName)"
        return await self._make_request("GET", endpoint)

    async def get_user_license_details(self, user_id: str) -> list[dict[str, Any]]:
        """Get assigned Microsoft 365 license details for a user."""
        endpoint = f"/users/{user_id}/licenseDetails"
        data = await self._make_request("GET", endpoint)
        return data.get("value", [])

    async def find_user_by_display_name(self, display_name: str) -> dict[str, Any] | None:
        """Find a Microsoft user by exact displayName."""
        if not display_name or not display_name.strip():
            return None

        escaped_name = display_name.strip().replace("'", "''")
        endpoint = (
            f"/users?$filter=displayName eq '{escaped_name}'&$select=id,userPrincipalName,displayName,mail&$top=2"
        )
        data = await self._make_request("GET", endpoint)
        users = data.get("value", [])

        if not users:
            return None

        return users[0]

    async def update_user(self, user_id: str, user_data: dict[str, Any]) -> None:
        """
        Update a user in Microsoft 365.

        user_data can include:
        - givenName (firstName)
        - surname (lastName)
        - displayName
        - jobTitle
        - department
        - officeLocation (office)
        - mobilePhone
        - businessPhones (array)
        - streetAddress
        - city
        - state
        - postalCode
        - country (or countryLetterCode)
        """
        endpoint = f"/users/{user_id}"

        # Filter out None values
        update_data = {k: v for k, v in user_data.items() if v is not None}
        if not update_data:
            return

        await self._make_request("PATCH", endpoint, update_data)

    async def set_user_manager(self, user_id: str, manager_user_id: str) -> None:
        """Set manager relation for a user in Microsoft Graph."""
        endpoint = f"/users/{user_id}/manager/$ref"
        payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{manager_user_id}"}
        await self._make_request("PUT", endpoint, payload)

    async def clear_user_manager(self, user_id: str) -> None:
        """Remove manager relation for a user in Microsoft Graph."""
        endpoint = f"/users/{user_id}/manager/$ref"
        await self._make_request("DELETE", endpoint)

    def map_graph_user_to_employee(self, graph_user: dict[str, Any]) -> dict[str, Any]:
        """Map Microsoft Graph user to Employee model."""
        business_phones = graph_user.get("businessPhones", [])
        office_phone = business_phones[0] if business_phones else None

        return {
            "azure_oid": graph_user.get("id"),
            "azure_upn": graph_user.get("userPrincipalName"),
            "first_name": graph_user.get("givenName"),
            "last_name": graph_user.get("surname"),
            "display_name": graph_user.get("displayName"),
            "title": graph_user.get("jobTitle"),
            "department": graph_user.get("department"),
            "office": graph_user.get("officeLocation"),
            "email": graph_user.get("mail") or graph_user.get("userPrincipalName"),
            "manager": graph_user.get("manager", {}).get("displayName") if graph_user.get("manager") else None,
            "manager_email": graph_user.get("manager", {}).get("mail")
            or graph_user.get("manager", {}).get("userPrincipalName")
            if graph_user.get("manager")
            else None,
            "mobile_phone": graph_user.get("mobilePhone"),
            "office_phone": office_phone,
            "street_address": graph_user.get("streetAddress"),
            "city": graph_user.get("city"),
            "state": graph_user.get("state"),
            "postal_code": graph_user.get("postalCode"),
            "country": graph_user.get("countryLetterCode") or graph_user.get("country"),
        }

    def map_employee_to_graph_user(self, employee_data: dict[str, Any]) -> dict[str, Any]:
        """Map Employee model to Microsoft Graph user update format."""
        graph_data = {}

        if employee_data.get("first_name"):
            graph_data["givenName"] = employee_data["first_name"]
        if employee_data.get("last_name"):
            graph_data["surname"] = employee_data["last_name"]
        if employee_data.get("display_name"):
            graph_data["displayName"] = employee_data["display_name"]
        if employee_data.get("title"):
            graph_data["jobTitle"] = employee_data["title"]
        if employee_data.get("department"):
            graph_data["department"] = employee_data["department"]
        if employee_data.get("office"):
            graph_data["officeLocation"] = employee_data["office"]
        if employee_data.get("mobile_phone"):
            graph_data["mobilePhone"] = employee_data["mobile_phone"]
        if employee_data.get("office_phone"):
            graph_data["businessPhones"] = [employee_data["office_phone"]]
        if employee_data.get("street_address"):
            graph_data["streetAddress"] = employee_data["street_address"]
        if employee_data.get("city"):
            graph_data["city"] = employee_data["city"]
        if employee_data.get("state"):
            graph_data["state"] = employee_data["state"]
        if employee_data.get("postal_code"):
            graph_data["postalCode"] = employee_data["postal_code"]
        if employee_data.get("country"):
            graph_data["country"] = employee_data["country"]

        return graph_data


# Singleton instance
graph_client = MicrosoftGraphClient()
