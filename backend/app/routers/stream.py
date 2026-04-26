"""
SSE (Server-Sent Events) router — GET /v1/stream/decisions

Gap 9: Redis Pub/Sub backend for distributed horizontal scaling.
       Falls back to in-process asyncio.Queue if Redis is unavailable.

Architecture:
  With    Redis: every worker publishes to channel `fg:{tenant_id}` and
                 subscribes to it — events cross worker boundaries.
  Without Redis: in-process queue (original behaviour) — single-worker only.

Env var:
  REDIS_URL=redis://localhost:6379/0   (unset = in-process fallback)
"""
import asyncio
import json
import logging
import os
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
# Gap 9 — Backend selection: Redis Pub/Sub or in-process Queue
# ---------------------------------------------------------------------------
_REDIS_URL: Optional[str] = os.environ.get("REDIS_URL")
_redis_available = False
_aioredis = None  # type: ignore

if _REDIS_URL:
    try:
        import aioredis as _aioredis_mod  # type: ignore
        _aioredis = _aioredis_mod
        _redis_available = True
        logger.info("Gap 9: Redis Pub/Sub enabled (%s)", _REDIS_URL)
    except ImportError:
        logger.warning("Gap 9: aioredis not installed — falling back to in-process queue.")
else:
    logger.info("Gap 9: REDIS_URL not set — using in-process pub/sub (single-worker mode).")

# In-process fallback: maps tenant_id → list[asyncio.Queue]
_subscribers: Dict[str, list] = {}


# ---------------------------------------------------------------------------
# publish_event — called from decisions.py after audit log creation
# ---------------------------------------------------------------------------
def publish_event(tenant_id: str, event: dict) -> None:
    """
    Publish an event to all connected SSE clients for this tenant.

    * If Redis is configured, the async Redis publish is scheduled as a
      fire-and-forget asyncio task on the current event loop.
    * Otherwise falls back to the in-process queue.
    """
    payload = json.dumps(event, default=str)

    if _redis_available:
        # Schedule non-blocking publish on the running loop
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(_redis_publish(tenant_id, payload))
        except RuntimeError:
            # No running loop (e.g., background thread) — skip gracefully
            pass
    else:
        _inproc_publish(tenant_id, payload)


def _inproc_publish(tenant_id: str, payload: str) -> None:
    """Push to all in-process subscriber queues."""
    queues = _subscribers.get(tenant_id, [])
    for q in queues:
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass  # slow client — drop rather than block


async def _redis_publish(tenant_id: str, payload: str) -> None:
    """Publish to Redis channel fg:<tenant_id>."""
    try:
        redis = await _aioredis.from_url(  # type: ignore
            _REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await redis.publish(f"fg:{tenant_id}", payload)
        await redis.close()
    except Exception as exc:
        logger.warning("Redis publish failed, falling back to in-process: %s", exc)
        _inproc_publish(tenant_id, payload)


# ---------------------------------------------------------------------------
# SSE generators
# ---------------------------------------------------------------------------
async def _inproc_generator(
    tenant_id: str,
    queue: asyncio.Queue,
) -> AsyncGenerator[str, None]:
    """In-process SSE generator — backfill + live queue drain."""
    try:
        recent = get_recent_audit_logs(tenant_id, limit=20)
        for record in reversed(recent):
            yield f"event: decision\ndata: {json.dumps(record, default=str)}\n\n"
    except Exception as exc:
        logger.warning("SSE backfill failed: %s", exc)

    while True:
        try:
            payload = await asyncio.wait_for(queue.get(), timeout=15.0)
            yield f"event: decision\ndata: {payload}\n\n"
        except asyncio.TimeoutError:
            yield ": heartbeat\n\n"  # keeps connection alive through proxies
        except asyncio.CancelledError:
            break


async def _redis_generator(tenant_id: str) -> AsyncGenerator[str, None]:
    """
    Gap 9 Redis SSE generator.
    Opens a persistent subscribe connection; restarts on transient errors.
    """
    try:
        recent = get_recent_audit_logs(tenant_id, limit=20)
        for record in reversed(recent):
            yield f"event: decision\ndata: {json.dumps(record, default=str)}\n\n"
    except Exception as exc:
        logger.warning("SSE backfill failed: %s", exc)

    channel = f"fg:{tenant_id}"
    reconnect_delay = 1.0

    while True:
        try:
            redis = await _aioredis.from_url(  # type: ignore
                _REDIS_URL, encoding="utf-8", decode_responses=True
            )
            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            reconnect_delay = 1.0  # reset on success

            while True:
                try:
                    msg = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=15.0)
                    if msg and msg["type"] == "message":
                        yield f"event: decision\ndata: {msg['data']}\n\n"
                    else:
                        yield ": heartbeat\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"

        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.warning("Redis SSE connection lost (%s) — retrying in %.1fs", exc, reconnect_delay)
            yield f"event: error\ndata: {{\"message\": \"Reconnecting...\"}}\n\n"
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 30.0)  # exponential back-off, cap 30s


# ---------------------------------------------------------------------------
# Auth dependency (supports ?token= query param for browser EventSource)
# ---------------------------------------------------------------------------
def _get_tenant(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    token: Optional[str] = Query(default=None, include_in_schema=False),
) -> str:
    raw = credentials.credentials if credentials else token
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
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/decisions", summary="SSE stream of real-time decision events")
async def stream_decisions(tenant_id: str = Depends(_get_tenant)):
    """
    SSE stream of real decision audit events for this tenant.

    Backend is automatically selected:
      REDIS_URL set   → Redis Pub/Sub (multi-worker safe)
      REDIS_URL unset → in-process asyncio.Queue (single-worker)

    Connect with:
      const es = new EventSource('/v1/stream/decisions', { ... });
      es.addEventListener('decision', (e) => ...);
    """
    _sse_headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",   # disable nginx buffering
        "Connection": "keep-alive",
    }

    if _redis_available:
        logger.info("SSE client connected via Redis: tenant=%s", tenant_id)
        return StreamingResponse(
            _redis_generator(tenant_id),
            media_type="text/event-stream",
            headers=_sse_headers,
        )

    # In-process path
    queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    _subscribers.setdefault(tenant_id, []).append(queue)
    logger.info("SSE client connected (in-proc): tenant=%s (total=%d)",
                tenant_id, len(_subscribers[tenant_id]))

    async def cleanup_generator():
        try:
            async for chunk in _inproc_generator(tenant_id, queue):
                yield chunk
        finally:
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
        headers=_sse_headers,
    )


@router.get("/analytics", summary="Real-time aggregate compliance stats")
async def get_analytics(tenant_id: str = Depends(_get_tenant)):
    """Real-time aggregate stats for the dashboard StatsOverview panel."""
    try:
        return get_tenant_analytics(tenant_id)
    except Exception as exc:
        logger.error("Analytics query failed: %s", exc)
        raise HTTPException(status_code=500, detail="Analytics unavailable.")
