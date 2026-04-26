"""
Webhook dispatcher — Phase 2 (Gap 4).

Fire-and-forget HTTP POST to registered webhook URLs.
Signs payload with HMAC-SHA256 if a secret is set.
Uses httpx with a 5-second timeout; failures are logged but never raised.

Usage:
    from app.services.webhook_dispatcher import dispatch_event
    await dispatch_event(tenant_id, "bias.detected", {"audit_id": ..., ...})
"""
import hashlib
import hmac
import json
import logging
from typing import Any, Dict

import httpx

from app.models.database import get_webhooks_for_event

logger = logging.getLogger(__name__)


async def dispatch_event(tenant_id: str, event_type: str, payload: Dict[str, Any]) -> None:
    """
    Deliver event_type to all registered webhooks for this tenant.
    Called as a BackgroundTask from decisions.py and drift.py.
    """
    hooks = get_webhooks_for_event(tenant_id, event_type)
    if not hooks:
        return

    body = json.dumps({"event": event_type, "tenant_id": tenant_id, "data": payload},
                      default=str)
    body_bytes = body.encode()

    async with httpx.AsyncClient(timeout=5.0) as client:
        for hook in hooks:
            headers = {"Content-Type": "application/json", "X-FairGuard-Event": event_type}

            # HMAC-SHA256 signature if secret is configured
            if hook.get("secret"):
                sig = hmac.new(
                    hook["secret"].encode(), body_bytes, hashlib.sha256
                ).hexdigest()
                headers["X-FairGuard-Signature"] = f"sha256={sig}"

            try:
                resp = await client.post(hook["url"], content=body_bytes, headers=headers)
                logger.info("Webhook %s → %s [%d]", event_type, hook["url"], resp.status_code)
            except Exception as exc:
                # Never let a failed webhook crash the decision pipeline
                logger.warning("Webhook delivery failed for %s: %s", hook["url"], exc)
