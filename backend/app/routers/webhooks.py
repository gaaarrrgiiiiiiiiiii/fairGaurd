"""
Webhooks router — Phase 2 (Gap 4).

Endpoints:
  POST   /v1/webhooks          — register a webhook (admin only)
  GET    /v1/webhooks          — list registered webhooks (auditor+)
  DELETE /v1/webhooks/{id}     — remove a webhook (admin only)
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.auth.rbac import TenantContext, admin_only, auditor_or_admin
from app.models.database import create_webhook, delete_webhook, list_webhooks

router = APIRouter()

_ALLOWED_EVENTS = {"bias.detected", "drift.detected", "correction.applied"}


class WebhookCreate(BaseModel):
    url: HttpUrl = Field(..., description="HTTPS endpoint to receive POST payloads.")
    events: List[str] = Field(
        default=["bias.detected"],
        description=f"Event types to subscribe to. Allowed: {sorted(_ALLOWED_EVENTS)}",
    )
    secret: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Optional signing secret. If set, payloads are HMAC-SHA256 signed.",
    )


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: str
    active: bool
    created_at: str


class WebhookCreated(BaseModel):
    id: str
    message: str


@router.post("", response_model=WebhookCreated, status_code=201, summary="Register webhook")
def register_webhook(
    body: WebhookCreate,
    ctx: TenantContext = Depends(admin_only),
):
    # Validate event types
    invalid = set(body.events) - _ALLOWED_EVENTS
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown event types: {sorted(invalid)}. Allowed: {sorted(_ALLOWED_EVENTS)}",
        )
    events_str = ",".join(sorted(set(body.events)))
    wh_id = create_webhook(
        tenant_id=ctx.tenant_id,
        url=str(body.url),
        events=events_str,
        secret=body.secret,
    )
    return WebhookCreated(id=wh_id, message=f"Webhook registered for events: {events_str}")


@router.get("", response_model=List[WebhookResponse], summary="List webhooks")
def get_webhooks(ctx: TenantContext = Depends(auditor_or_admin)):
    rows = list_webhooks(ctx.tenant_id)
    return [WebhookResponse(**r) for r in rows]


@router.delete("/{webhook_id}", status_code=204, summary="Delete webhook")
def remove_webhook(
    webhook_id: str,
    ctx: TenantContext = Depends(admin_only),
):
    deleted = delete_webhook(ctx.tenant_id, webhook_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Webhook not found.")
