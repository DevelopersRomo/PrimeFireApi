from datetime import datetime, timedelta
from typing import Any

import httpx

from core.config import settings


class MicrosoftGraphClient:
    """
    Client for Microsoft Graph API to manage users
    Requires App Registration with User.Read.All and User.ReadWrite.All permissions.
    """

    def __init__(self) -> None:
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self._token: str | None = None
        self._token_expiry: datetime | None = None

    async def _get_access_token(self) -> str:
        """Get access token using client credentials flow."""
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
            self._token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600) - 300)  # noqa: DTZ005

            return self._token

    async def _make_request(self, method: str, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make authenticated request to Graph API."""
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

            response.raise_for_status()

            if response.status_code == 204:
                return {}

            return response.json()

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

    async def update_user(self, user_id: str, user_data: dict[str, Any]) -> dict[str, Any]:
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

        # Filter out None values and fields that can't be updated
        update_data = {k: v for k, v in user_data.items() if v is not None}

        await self._make_request("PATCH", endpoint, update_data)

        # Return updated user
        return await self.get_user(user_id)

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
            "AzureOid": graph_user.get("id"),
            "AzureUpn": graph_user.get("userPrincipalName"),
            "FirstName": graph_user.get("givenName"),
            "LastName": graph_user.get("surname"),
            "DisplayName": graph_user.get("displayName"),
            "Title": graph_user.get("jobTitle"),
            "Department": graph_user.get("department"),
            "Office": graph_user.get("officeLocation"),
            "Email": graph_user.get("mail") or graph_user.get("userPrincipalName"),
            "Manager": graph_user.get("manager", {}).get("displayName") if graph_user.get("manager") else None,
            "ManagerEmail": graph_user.get("manager", {}).get("mail")
            or graph_user.get("manager", {}).get("userPrincipalName")
            if graph_user.get("manager")
            else None,
            "MobilePhone": graph_user.get("mobilePhone"),
            "OfficePhone": office_phone,
            "StreetAddress": graph_user.get("streetAddress"),
            "City": graph_user.get("city"),
            "State": graph_user.get("state"),
            "PostalCode": graph_user.get("postalCode"),
            "Country": graph_user.get("countryLetterCode") or graph_user.get("country"),
        }

    def map_employee_to_graph_user(self, employee_data: dict[str, Any]) -> dict[str, Any]:
        """Map Employee model to Microsoft Graph user update format."""
        graph_data = {}

        if employee_data.get("FirstName"):
            graph_data["givenName"] = employee_data["FirstName"]
        if employee_data.get("LastName"):
            graph_data["surname"] = employee_data["LastName"]
        if employee_data.get("DisplayName"):
            graph_data["displayName"] = employee_data["DisplayName"]
        if employee_data.get("Title"):
            graph_data["jobTitle"] = employee_data["Title"]
        if employee_data.get("Department"):
            graph_data["department"] = employee_data["Department"]
        if employee_data.get("Office"):
            graph_data["officeLocation"] = employee_data["Office"]
        if employee_data.get("MobilePhone"):
            graph_data["mobilePhone"] = employee_data["MobilePhone"]
        if employee_data.get("OfficePhone"):
            graph_data["businessPhones"] = [employee_data["OfficePhone"]]
        if employee_data.get("StreetAddress"):
            graph_data["streetAddress"] = employee_data["StreetAddress"]
        if employee_data.get("City"):
            graph_data["city"] = employee_data["City"]
        if employee_data.get("State"):
            graph_data["state"] = employee_data["State"]
        if employee_data.get("PostalCode"):
            graph_data["postalCode"] = employee_data["PostalCode"]
        if employee_data.get("Country"):
            graph_data["country"] = employee_data["Country"]

        return graph_data


# Singleton instance
graph_client = MicrosoftGraphClient()
