"""
Audit router — Phase 1C.

Endpoints:
  GET /v1/audit/verify   — verify hash-chain integrity for the tenant's logs
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.auth.jwt_handler import verify_token
from app.models.database import verify_audit_chain

router = APIRouter()


def get_current_tenant(authorization: str = Header(default=None)) -> str:
    tenant = verify_token(authorization)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid or missing token.")
    return tenant


class ChainVerifyResponse(BaseModel):
    valid: bool
    records_checked: int
    first_violation: Optional[str] = None
    message: str


@router.get("/verify", response_model=ChainVerifyResponse, summary="Verify audit log integrity")
def verify_chain(tenant_id: str = Depends(get_current_tenant)):
    """
    Walks the SHA-256 hash chain for this tenant's audit logs.
    Returns valid=True if every record's hash is consistent with its predecessor.
    A tampered or deleted record will break the chain and report first_violation.
    """
    result = verify_audit_chain(tenant_id)
    return ChainVerifyResponse(
        valid=result["valid"],
        records_checked=result["records_checked"],
        first_violation=result["first_violation"],
        message=(
            f"Chain intact across {result['records_checked']} records."
            if result["valid"]
            else f"Chain broken at record {result['first_violation']}."
        ),
    )
