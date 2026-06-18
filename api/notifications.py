"""Notification API endpoints."""

import hashlib
import time
from asyncio import Lock
from collections import deque
from secrets import compare_digest

import httpx
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlmodel import Session

from api.dependencies import get_current_employee
from bd.dependencies import get_db
from core.config import settings
from schemas.notifications import (
    ContactPrimeFireRequest,
    ContactPrimeFireResponse,
    NotificationRequestWrapper,
)
from services.notifications.contact_primefire import send_contact_primefire_notification
from services.notifications.forms import send_form_notification
from services.notifications.notifications import (
    notify_ticket_created,
    notify_ticket_message,
    notify_time_off_approved,
    notify_time_off_rejected,
    notify_user_approved,
    send_custom_notification,
)
from services.notifications.schemas import NotificationField, NotificationResponse

router = APIRouter()

_CONTACT_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = {}
_CONTACT_DUPLICATE_INDEX: dict[str, float] = {}
_CONTACT_DUPLICATE_QUEUE: deque[tuple[float, str]] = deque()
_CONTACT_SPAM_GUARD_LOCK = Lock()


def _get_allowed_turnstile_hostnames() -> set[str]:
    hostnames_raw = getattr(settings, "CLOUDFLARE_TURNSTILE_ALLOWED_HOSTNAMES", "")
    if not hostnames_raw:
        return set()

    return {hostname.strip().lower() for hostname in hostnames_raw.split(",") if hostname.strip()}


def _extract_client_ip(http_request: Request) -> str:
    forwarded_for = http_request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        forwarded_ip = forwarded_for.split(",")[0].strip()
        if forwarded_ip:
            return forwarded_ip

    real_ip = http_request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    if http_request.client and http_request.client.host:
        return http_request.client.host.strip()

    return "unknown"


def _build_contact_fingerprint(request: ContactPrimeFireRequest) -> str:
    components = [
        (request.name or "").strip().lower(),
        str(request.email).strip().lower(),
        "".join(char for char in request.phone if char.isdigit()),
        (request.subject or "").strip().lower(),
        (request.note or "").strip().lower(),
        (request.company or "").strip().lower(),
        (request.industry or "").strip().lower(),
        (request.service or "").strip().lower(),
    ]
    payload = "|".join(components)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def _enforce_contact_spam_protections(request: ContactPrimeFireRequest, client_ip: str) -> None:
    if request.website and request.website.strip():
        raise HTTPException(status_code=400, detail="Spam detected")

    max_requests = max(1, int(getattr(settings, "CONTACT_PRIMEFIRE_RATE_LIMIT_MAX_REQUESTS", 3)))
    rate_window_seconds = max(60, int(getattr(settings, "CONTACT_PRIMEFIRE_RATE_LIMIT_WINDOW_SECONDS", 600)))
    duplicate_window_seconds = max(60, int(getattr(settings, "CONTACT_PRIMEFIRE_DUPLICATE_WINDOW_SECONDS", 600)))

    now = time.monotonic()
    fingerprint = _build_contact_fingerprint(request)

    async with _CONTACT_SPAM_GUARD_LOCK:
        bucket = _CONTACT_RATE_LIMIT_BUCKETS.setdefault(client_ip, deque())

        rate_cutoff = now - rate_window_seconds
        while bucket and bucket[0] <= rate_cutoff:
            bucket.popleft()

        if len(bucket) >= max_requests:
            retry_after = max(1, int(rate_window_seconds - (now - bucket[0])))
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for this IP",
                headers={"Retry-After": str(retry_after)},
            )

        # Count the attempt immediately so repeated spam attempts also consume quota.
        bucket.append(now)

        duplicate_cutoff = now - duplicate_window_seconds
        while _CONTACT_DUPLICATE_QUEUE and _CONTACT_DUPLICATE_QUEUE[0][0] <= duplicate_cutoff:
            queued_timestamp, queued_fingerprint = _CONTACT_DUPLICATE_QUEUE.popleft()
            if _CONTACT_DUPLICATE_INDEX.get(queued_fingerprint) == queued_timestamp:
                _CONTACT_DUPLICATE_INDEX.pop(queued_fingerprint, None)

        if fingerprint in _CONTACT_DUPLICATE_INDEX:
            raise HTTPException(
                status_code=409,
                detail="Duplicate contact submission detected. Please wait before sending the same request again",
            )

        _CONTACT_DUPLICATE_INDEX[fingerprint] = now
        _CONTACT_DUPLICATE_QUEUE.append((now, fingerprint))


def _extract_contact_token(
    authorization: str | None,
    x_contact_token: str | None,
) -> str | None:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token.strip()

    if x_contact_token:
        return x_contact_token.strip()

    return None


async def _verify_turnstile_token(turnstile_token: str, http_request: Request) -> None:
    turnstile_secret = getattr(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", "").strip()
    if not turnstile_secret:
        raise HTTPException(status_code=503, detail="Captcha validation is not configured")

    remote_ip = _extract_client_ip(http_request)

    verification_payload: dict[str, str] = {
        "secret": turnstile_secret,
        "response": turnstile_token,
    }
    if remote_ip and remote_ip != "unknown":
        verification_payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            verification_response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data=verification_payload,
            )
            verification_response.raise_for_status()
            verification_data = verification_response.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Captcha verification service unavailable") from exc

    if not verification_data.get("success", False):
        raise HTTPException(status_code=400, detail="Captcha verification failed")

    allowed_hostnames = _get_allowed_turnstile_hostnames()
    verified_hostname = str(verification_data.get("hostname", "")).strip().lower()
    if allowed_hostnames and verified_hostname not in allowed_hostnames:
        raise HTTPException(status_code=400, detail="Captcha hostname is not allowed")


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequestWrapper,
    current_employee=Depends(get_current_employee),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    """
    Send a notification email.

    Supports multiple notification types:
    - custom: Generic notification with custom fields
    - time_off_approved: Time off request approved
    - time_off_rejected: Time off request rejected
    - ticket_created: New ticket created
    - ticket_message: New comment on ticket
    - user_approved: User account approved
    - form: Form notification (backward compatibility)

    Requires authentication.
    """
    try:  # noqa: PLW0717
        if request.notification_type == "custom":
            if not request.custom:
                raise HTTPException(
                    status_code=400,
                    detail="custom notification data is required",
                )

            custom_fields = None
            if request.custom.fields:
                custom_fields = [
                    NotificationField(label=field["label"], value=field["value"]) for field in request.custom.fields
                ]

            return await send_custom_notification(
                title=request.custom.title,
                message_body=request.custom.message_body,
                to_email=request.custom.to_email,
                cc_email=request.custom.cc_email,
                action_type=request.custom.action_type,
                sub_title=request.custom.sub_title,
                performed_by_name=request.custom.performed_by_name,
                performed_by_email=request.custom.performed_by_email,
                fields=custom_fields,
                action_url=request.custom.action_url,
                action_text=request.custom.action_text,
            )

        if request.notification_type == "time_off_approved":
            if not request.time_off_approved:
                raise HTTPException(
                    status_code=400,
                    detail="time_off_approved notification data is required",
                )

            return await notify_time_off_approved(
                request_id=request.time_off_approved.request_id,
                employee_id=request.time_off_approved.employee_id,
                employee_name=request.time_off_approved.employee_name,
                employee_email=request.time_off_approved.employee_email,
                absence_type=request.time_off_approved.absence_type,
                start_date=request.time_off_approved.start_date,
                end_date=request.time_off_approved.end_date,
                total_days=request.time_off_approved.total_days,
                total_hours=request.time_off_approved.total_hours,
                reason=request.time_off_approved.reason,
                reviewed_by_name=request.time_off_approved.reviewed_by_name,
                reviewed_by_email=request.time_off_approved.reviewed_by_email,
                review_notes=request.time_off_approved.review_notes,
                action_url=request.time_off_approved.action_url,
            )

        if request.notification_type == "time_off_rejected":
            if not request.time_off_rejected:
                raise HTTPException(
                    status_code=400,
                    detail="time_off_rejected notification data is required",
                )

            return await notify_time_off_rejected(
                request_id=request.time_off_rejected.request_id,
                employee_id=request.time_off_rejected.employee_id,
                employee_name=request.time_off_rejected.employee_name,
                employee_email=request.time_off_rejected.employee_email,
                absence_type=request.time_off_rejected.absence_type,
                start_date=request.time_off_rejected.start_date,
                end_date=request.time_off_rejected.end_date,
                total_days=request.time_off_rejected.total_days,
                total_hours=request.time_off_rejected.total_hours,
                reason=request.time_off_rejected.reason,
                reviewed_by_name=request.time_off_rejected.reviewed_by_name,
                reviewed_by_email=request.time_off_rejected.reviewed_by_email,
                review_notes=request.time_off_rejected.review_notes,
                action_url=request.time_off_rejected.action_url,
            )

        if request.notification_type == "ticket_created":
            if not request.ticket_created:
                raise HTTPException(
                    status_code=400,
                    detail="ticket_created notification data is required",
                )

            creator_notification, assignee_notification = await notify_ticket_created(
                ticket_id=request.ticket_created.ticket_id,
                title=request.ticket_created.title,
                description=request.ticket_created.description,
                status=request.ticket_created.status,
                priority=request.ticket_created.priority,
                created_by_name=request.ticket_created.created_by_name,
                created_by_email=request.ticket_created.created_by_email,
                assigned_to_name=request.ticket_created.assigned_to_name,
                assigned_to_email=request.ticket_created.assigned_to_email,
                action_url=request.ticket_created.action_url,
                notify_assignee=request.notify_assignee,
            )

            return creator_notification

        if request.notification_type == "ticket_message":
            if not request.ticket_message:
                raise HTTPException(
                    status_code=400,
                    detail="ticket_message notification data is required",
                )

            if not request.commenter_id:
                raise HTTPException(
                    status_code=400,
                    detail="commenter_id is required for ticket_message notifications",
                )

            if not request.ticket_creator_id or not request.ticket_creator_email:
                raise HTTPException(
                    status_code=400,
                    detail="ticket_creator_id and ticket_creator_email are required for ticket_message notifications",
                )

            creator_notification, assignee_notification = await notify_ticket_message(
                ticket_id=request.ticket_message.ticket_id,
                ticket_title=request.ticket_message.ticket_title,
                message_id=request.ticket_message.message_id,
                message_text=request.ticket_message.message_text,
                commenter_id=request.commenter_id,
                commenter_name=request.ticket_message.commenter_name,
                commenter_email=request.ticket_message.commenter_email,
                ticket_creator_id=request.ticket_creator_id,
                ticket_creator_email=request.ticket_creator_email,
                ticket_assigned_to_id=request.ticket_assigned_to_id,
                ticket_assigned_to_email=request.ticket_assigned_to_email,
                action_url=request.ticket_message.action_url,
            )

            return (
                creator_notification
                or assignee_notification
                or NotificationResponse(
                    success=True,
                    message_id=None,
                )
            )

        if request.notification_type == "user_approved":
            if not request.user_approved:
                raise HTTPException(
                    status_code=400,
                    detail="user_approved notification data is required",
                )

            return await notify_user_approved(
                user_id=request.user_approved.user_id,
                user_name=request.user_approved.user_name,
                user_email=request.user_approved.user_email,
                approved_by_name=request.user_approved.approved_by_name,
                approved_by_email=request.user_approved.approved_by_email,
                action_url=request.user_approved.action_url,
            )

        if request.notification_type == "form":
            if not request.form:
                raise HTTPException(
                    status_code=400,
                    detail="form notification data is required",
                )

            return await send_form_notification(notification_data=request.form)  # type: ignore[return-value]

        raise HTTPException(
            status_code=400,
            detail=f"Unknown notification type: {request.notification_type}",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {e!s}",
        )


@router.post("/send/contact-primefire", response_model=ContactPrimeFireResponse)
async def send_contact_primefire(
    request: ContactPrimeFireRequest,
    http_request: Request,
    authorization: str | None = Header(default=None),
    x_contact_token: str | None = Header(default=None),
) -> ContactPrimeFireResponse:
    """Send PrimeFire contact template email with dedicated static token auth."""
    received_token = _extract_contact_token(authorization, x_contact_token)
    configured_token = getattr(settings, "CONTACT_PRIMEFIRE_API_TOKEN", "")

    if not received_token or not configured_token or not compare_digest(received_token, configured_token):
        raise HTTPException(status_code=401, detail="Invalid or missing contact endpoint token")

    client_ip = _extract_client_ip(http_request)
    await _enforce_contact_spam_protections(request, client_ip)

    await _verify_turnstile_token(request.cf_turnstile_response, http_request)

    notification_result = await send_contact_primefire_notification(request)
    if not notification_result.success:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "delivery_failed",
                "message": notification_result.error_message or "Unable to send contact-primefire notification",
            },
        )

    return ContactPrimeFireResponse(
        success=True,
        status="sent",
        message="Contact PrimeFire notification sent successfully",
        message_id=notification_result.message_id,
    )
