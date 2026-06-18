"""Teams notification functions using Microsoft Graph API.

REQUIRED PERMISSIONS:
The Azure App Registration needs the following Microsoft Graph API permissions (Application permissions):
- Chat.ReadWrite.All (this includes permissions to read, create chats, and send messages)

NOTE: ChatMessage.Send is only available as a Delegated permission, not Application permission.
Chat.ReadWrite.All (Application permission) is sufficient for sending chat messages.

Steps to configure:
1. Go to Azure Portal > App Registrations > Your App
2. Click "API Permissions"
3. Click "Add a permission"
4. Select "Microsoft Graph"
5. Select "Application permissions"
6. Search and add:
   - Chat.ReadWrite.All
7. Click "Grant admin consent for [Your Tenant]"

IMPORTANT: The BOT_EMAIL account must have a Teams license and be able to use Teams.

NOTE: All notifications are sent using BOT_EMAIL as the sender (orchestrator).
"""

import asyncio
import logging

import httpx

from core.config import settings
from services.notifications.auth import get_graph_api_auth_headers
from services.notifications.schemas import NotificationResponse

logger = logging.getLogger(__name__)


def get_retry_client() -> httpx.AsyncClient:
    """Get HTTP client with retry logic."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    )


async def get_user_id_by_email(user_email: str) -> str | None:
    """
    Get Microsoft Graph user ID by email address.

    Args:
        user_email: Email address of the user

    Returns:
        User ID (object ID) or None if not found
    """
    headers = await get_graph_api_auth_headers()
    if not headers:
        logger.error("Failed to get authentication headers")
        return None

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}"

    try:
        async with get_retry_client() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            user_data = response.json()
            return user_data.get("id")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logger.warning(f"User not found: {user_email}")
        else:
            logger.exception(f"Error getting user ID: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.exception(f"Error getting user ID: {e!s}")
        return None


async def get_or_create_chat(user_email: str, recipient_email: str) -> str | None:
    """
    Get or create a 1:1 chat between two users.

    Args:
        user_email: Email of the bot/user sending the message (BOT_EMAIL)
        recipient_email: Email of the recipient

    Returns:
        Chat ID or None if failed
    """
    headers = await get_graph_api_auth_headers()
    if not headers:
        logger.error("Failed to get authentication headers")
        return None

    # Get user IDs
    bot_user_id = await get_user_id_by_email(user_email)
    recipient_user_id = await get_user_id_by_email(recipient_email)

    if not bot_user_id or not recipient_user_id:
        logger.error(f"Failed to get user IDs. Bot: {bot_user_id}, Recipient: {recipient_user_id}")
        return None

    try:
        return await _get_or_create_chat(headers, bot_user_id, recipient_user_id)

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        logger.exception(f"Error getting/creating chat: {e.response.status_code} - {error_text}")

        # Check for missing permissions error
        if e.response.status_code == 403:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", "")
                if (
                    "Chat.ReadBasic.All" in error_msg
                    or "Chat.Read.All" in error_msg
                    or "Chat.ReadWrite.All" in error_msg
                ):
                    logger.exception(
                        "MISSING PERMISSIONS: The Azure App Registration needs the following Microsoft Graph API permission:\n"
                        "- Chat.ReadWrite.All (Application permission)\n\n"
                        "This permission must be granted admin consent in Azure Portal:\n"
                        "Azure Portal > App Registrations > Your App > API Permissions > Add Permission > Microsoft Graph > Application Permissions > Chat.ReadWrite.All\n\n"
                        "NOTE: ChatMessage.Send is only available as Delegated permission. Chat.ReadWrite.All (Application) is sufficient."
                    )
            except Exception:
                pass
        return None
    except Exception as e:
        logger.exception(f"Error getting/creating chat: {e!s}")
        return None


def _find_one_on_one_chat(chats_data: dict, recipient_user_id: str) -> str | None:
    for chat in chats_data.get("value", []):
        if chat.get("chatType") != "oneOnOne":
            continue
        for member in chat.get("members", []):
            if member.get("id") == recipient_user_id:
                return chat.get("id")
    return None


def _one_on_one_chat_payload(bot_user_id: str, recipient_user_id: str) -> dict:
    return {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{bot_user_id}')",
            },
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{recipient_user_id}')",
            },
        ],
    }


async def _get_or_create_chat(
    headers: dict[str, str],
    bot_user_id: str,
    recipient_user_id: str,
) -> str | None:
    url = f"https://graph.microsoft.com/v1.0/users/{bot_user_id}/chats"
    async with get_retry_client() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        existing_chat_id = _find_one_on_one_chat(response.json(), recipient_user_id)
        if existing_chat_id:
            return existing_chat_id

        response = await client.post(
            "https://graph.microsoft.com/v1.0/chats",
            headers=headers,
            json=_one_on_one_chat_payload(bot_user_id, recipient_user_id),
        )
        response.raise_for_status()
        return response.json().get("id")


async def send_teams_message(
    *,
    recipient_email: str,
    message: str,
    sender_email: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Send a Teams chat message to a user.

    NOTE: sender_email should always be BOT_EMAIL (the orchestrator).
    All notifications are sent from BOT_EMAIL, even though actions may be performed by different users.

    Args:
        recipient_email: Email address of the recipient
        message: Message content (supports HTML)
        sender_email: Email of the sender (defaults to BOT_EMAIL)

    Returns:
        (success: bool, message_id: str | None, error_message: str | None)
    """
    sender_email = sender_email or getattr(settings, "BOT_EMAIL", None)
    if not sender_email:
        return False, None, "No sender email configured (BOT_EMAIL)"

    headers = await get_graph_api_auth_headers()
    if not headers:
        return False, None, "Failed to get authentication headers"

    # Get or create chat
    chat_id = await get_or_create_chat(sender_email, recipient_email)
    if not chat_id:
        error_msg = (
            f"Failed to get or create chat with {recipient_email}. "
            "Check logs for details. "
            "Required permission: Chat.ReadWrite.All (Application permission in Azure)"
        )
        return False, None, error_msg

    # Send message
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"

    message_data = {"body": {"contentType": "html", "content": message}}

    max_retries = 3
    last_error = None

    async with get_retry_client() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url, headers=headers, json=message_data)
                response.raise_for_status()

                message_response = response.json()
                message_id = message_response.get("id")

                logger.info(f"Teams message sent successfully to {recipient_email}. Message ID: {message_id}")
                return True, message_id, None

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                if e.response.status_code < 500:
                    break
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {last_error}")

            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)

    error_msg = f"Failed to send Teams message after {max_retries} attempts: {last_error}"
    logger.error(error_msg)
    return False, None, error_msg


async def send_teams_notification(
    *,
    recipient_email: str,
    title: str,
    message_body: str,
    action_url: str | None = None,
    action_text: str = "View Details",
    sender_email: str | None = None,
) -> NotificationResponse:
    """
    Send a Teams notification with formatted message.

    Always uses BOT_EMAIL as sender (orchestrator).

    Args:
        recipient_email: Email address of the recipient
        title: Notification title
        message_body: Main message content
        action_url: Optional URL for action button
        action_text: Text for action button
        sender_email: Email of the sender (defaults to BOT_EMAIL, ignored)

    Returns:
        NotificationResponse with success status
    """
    try:
        # Format message as HTML
        html_message = f"""
        <div style="font-family: Segoe UI, sans-serif;">
            <h2 style="color: #0078d4; margin-bottom: 10px;">{title}</h2>
            <p style="margin-bottom: 15px;">{message_body}</p>
            {f'<p><a href="{action_url}" style="background-color: #0078d4; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">{action_text}</a></p>' if action_url else ""}
        </div>
        """

        success, message_id, error_message = await send_teams_message(
            recipient_email=recipient_email,
            message=html_message,
            sender_email=sender_email,
        )

        if success:
            return NotificationResponse(success=True, message_id=message_id)
        return NotificationResponse(success=False, error_message=error_message)

    except Exception as e:
        return NotificationResponse(
            success=False,
            error_message=f"Error sending Teams notification: {e!s}",
        )
