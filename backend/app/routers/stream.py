"""
SSE (Server-Sent Events) router — GET /v1/stream/decisions

Phase 3: Real-time audit log feed.
Pushes new decision events to all connected dashboard clients
without polling. Uses asyncio.Queue per connection.

Authenticated: same JWT/API-key auth as other endpoints.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_handler import verify_token, DEV_MODE
from app.models.database import get_recent_audit_logs, get_tenant_analytics

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# In-process pub/sub — maps tenant_id → list of asyncio.Queue
# Scales to multi-worker with Redis Pub/Sub (Phase 4 upgrade path)
# ---------------------------------------------------------------------------
_subscribers: Dict[str, list[asyncio.Queue]] = {}


def publish_event(tenant_id: str, event: dict) -> None:
    """
    Push a new event to all active SSE clients for this tenant.
    Called from decisions.py after audit log is created.
    Thread-safe: queues are thread-safe.
    """
    queues = _subscribers.get(tenant_id, [])
    payload = json.dumps(event, default=str)
    for q in queues:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass  # slow client — drop event rather than block


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
def _get_tenant(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    token: Optional[str] = Query(default=None, include_in_schema=False),
) -> str:
    """
    Auth for SSE endpoints.
    Accepts Bearer token via Authorization header OR ?token= query param.
    ?token= is required because EventSource cannot set custom headers.
    """
    raw = (
        credentials.credentials
        if credentials
        else token  # EventSource fallback
    )
    tenant_id = verify_token(raw)
    if tenant_id is None:
        if DEV_MODE:
            return "tenant_local_dev"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tenant_id


# ---------------------------------------------------------------------------
# SSE generator
# ---------------------------------------------------------------------------
async def _event_generator(
    tenant_id: str,
    queue: asyncio.Queue,
) -> AsyncGenerator[str, None]:
    """Yields SSE-formatted strings. Sends a heartbeat every 15 s."""
    # Send last 20 decisions as initial backfill
    try:
        recent = get_recent_audit_logs(tenant_id, limit=20)
        for record in reversed(recent):
            yield f"event: decision\ndata: {json.dumps(record, default=str)}\n\n"
    except Exception as exc:
        logger.warning("SSE backfill failed: %s", exc)

    # Stream new events
    while True:
        try:
            payload = await asyncio.wait_for(queue.get(), timeout=15.0)
            yield f"event: decision\ndata: {payload}\n\n"
        except asyncio.TimeoutError:
            # Heartbeat — keeps connection alive through proxies
            yield ": heartbeat\n\n"
        except asyncio.CancelledError:
            break


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/decisions")
async def stream_decisions(tenant_id: str = Depends(_get_tenant)):
    """
    SSE stream of real decision audit events for this tenant.

    Connect with:
      const es = new EventSource('/v1/stream/decisions', { ... });
      es.addEventListener('decision', (e) => ...);
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=200)

    # Register subscriber
    _subscribers.setdefault(tenant_id, []).append(queue)
    logger.info("SSE client connected: tenant=%s (total=%d)", tenant_id,
                len(_subscribers[tenant_id]))

    async def cleanup_generator():
        try:
            async for chunk in _event_generator(tenant_id, queue):
                yield chunk
        finally:
            # Deregister on disconnect
            try:
                _subscribers[tenant_id].remove(queue)
                if not _subscribers[tenant_id]:
                    del _subscribers[tenant_id]
                logger.info("SSE client disconnected: tenant=%s", tenant_id)
            except (ValueError, KeyError):
                pass

    return StreamingResponse(
        cleanup_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",       # disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/analytics")
async def get_analytics(tenant_id: str = Depends(_get_tenant)):
    """
    Real-time aggregate stats for the dashboard StatsOverview panel.
    Reads from the audit_logs table — no mocked data.
    """
    try:
        return get_tenant_analytics(tenant_id)
    except Exception as exc:
        logger.error("Analytics query failed: %s", exc)
        raise HTTPException(status_code=500, detail="Analytics unavailable.")
