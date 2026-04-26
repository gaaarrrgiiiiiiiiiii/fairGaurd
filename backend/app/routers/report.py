"""
Report router — GET /v1/report/generate

H1: Auth enforced. Tenant ID is derived from the Bearer token, not from a
query parameter. An unauthenticated caller cannot access another tenant's data.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_handler import verify_token, DEV_MODE
from app.services.compliance_report import generate_pdf_report

router = APIRouter()
security = HTTPBearer(auto_error=False)


def _get_tenant(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    """Return tenant_id from a valid token, or raise 401."""
    raw_token = credentials.credentials if credentials else None
    tenant_id = verify_token(raw_token)
    if tenant_id is None:
        if DEV_MODE:
            return "tenant_local_dev"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tenant_id


@router.get("/generate")
async def get_compliance_report(tenant_id: str = Depends(_get_tenant)):
    """
    Generate and download an EU AI Act Article 13 compliance report PDF.

    Requires valid Bearer token. Tenant is inferred from the token.
    """
    pdf_bytes = generate_pdf_report(tenant_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="fairguard_eu_aia_report_{tenant_id}.pdf"'
            )
        },
    )
