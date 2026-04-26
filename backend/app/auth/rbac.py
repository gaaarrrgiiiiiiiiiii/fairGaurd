"""
RBAC dependency helpers — Phase 2 (Gap 3).

Usage in a router:
    from app.auth.rbac import require_role, TenantContext

    @router.put("/settings")
    def my_endpoint(ctx: TenantContext = Depends(require_role("admin"))):
        tenant_id = ctx.tenant_id
        role      = ctx.role

Roles (ascending privilege):
    viewer   — read audit logs and analytics
    auditor  — viewer + download compliance reports
    admin    — full access including threshold configuration
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_handler import verify_token, DEV_MODE

_security = HTTPBearer(auto_error=False)

_ROLE_RANK = {"viewer": 0, "auditor": 1, "admin": 2}


@dataclass
class TenantContext:
    tenant_id: str
    role: str


def _extract_tenant(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(_security),
    token: Optional[str] = Header(default=None, alias="authorization"),
) -> TenantContext:
    """
    Resolve Bearer token to (tenant_id, role).
    Accepts Authorization header only (not query param — use stream.py for SSE).
    """
    raw = credentials.credentials if credentials else token
    result = verify_token(raw)

    if result is None:
        if DEV_MODE:
            return TenantContext(tenant_id="tenant_local_dev", role="admin")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tenant_id, role = result
    return TenantContext(tenant_id=tenant_id, role=role)


def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory. Returns a Depends() that enforces role.

        ctx = Depends(require_role("admin", "auditor"))

    Raises 403 if the authenticated role is not in allowed_roles.
    """
    allowed = set(allowed_roles)

    def _dep(ctx: TenantContext = Depends(_extract_tenant)) -> TenantContext:
        if ctx.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{ctx.role}' is not authorised for this action. "
                    f"Required: {sorted(allowed)}"
                ),
            )
        return ctx

    return _dep


# Convenience shorthands
any_authenticated   = require_role("viewer", "auditor", "admin")
auditor_or_admin    = require_role("auditor", "admin")
admin_only          = require_role("admin")
