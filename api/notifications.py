"""Notification API endpoints."""

from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session
from typing import Optional

from api.dependencies import get_current_employee, require_authentication
from core.config import settings
from bd.dependencies import get_db
from schemas.notifications import (
    ContactPrimeFireRequest,
    ContactPrimeFireResponse,
    NotificationRequestWrapper,
)
from services.notifications.contact_primefire import send_contact_primefire_notification
from services.notifications.notifications import (
    send_custom_notification,
    notify_time_off_approved,
    notify_time_off_rejected,
    notify_ticket_created,
    notify_ticket_message,
    notify_user_approved,
)
from services.notifications.forms import send_form_notification
from services.notifications.schemas import NotificationResponse, NotificationField

router = APIRouter()


def _extract_contact_token(
    authorization: Optional[str],
    x_contact_token: Optional[str],
) -> Optional[str]:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token.strip()

    if x_contact_token:
        return x_contact_token.strip()

    return None


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
    try:
        if request.notification_type == "custom":
            if not request.custom:
                raise HTTPException(
                    status_code=400,
                    detail="custom notification data is required",
                )
            
            custom_fields = None
            if request.custom.fields:
                custom_fields = [
                    NotificationField(label=field["label"], value=field["value"])
                    for field in request.custom.fields
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

        elif request.notification_type == "time_off_approved":
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

        elif request.notification_type == "time_off_rejected":
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

        elif request.notification_type == "ticket_created":
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

        elif request.notification_type == "ticket_message":
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
            
            return creator_notification or assignee_notification or NotificationResponse(
                success=True,
                message_id=None,
            )

        elif request.notification_type == "user_approved":
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

        elif request.notification_type == "form":
            if not request.form:
                raise HTTPException(
                    status_code=400,
                    detail="form notification data is required",
                )
            
            return await send_form_notification(notification_data=request.form)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown notification type: {request.notification_type}",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}",
        )


@router.post("/send/contact-primefire", response_model=ContactPrimeFireResponse)
async def send_contact_primefire(
    request: ContactPrimeFireRequest,
    authorization: Optional[str] = Header(default=None),
    x_contact_token: Optional[str] = Header(default=None),
) -> ContactPrimeFireResponse:
    """Send PrimeFire contact template email with dedicated static token auth."""
    received_token = _extract_contact_token(authorization, x_contact_token)
    configured_token = getattr(settings, "CONTACT_PRIMEFIRE_API_TOKEN", "")

    if not received_token or not configured_token or not compare_digest(received_token, configured_token):
        raise HTTPException(status_code=401, detail="Invalid or missing contact endpoint token")

    notification_result = await send_contact_primefire_notification(request)
    if not notification_result.success:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "delivery_failed",
                "message": notification_result.error_message
                or "Unable to send contact-primefire notification",
            },
        )

    return ContactPrimeFireResponse(
        success=True,
        status="sent",
        message="Contact PrimeFire notification sent successfully",
        message_id=notification_result.message_id,
    )

