"""
Auth router — issue JWT tokens for tenants.

POST /v1/auth/token
  Body: { "tenant_id": "...", "api_key": "sk_fgt_..." }
  Response: { "access_token": "eyJ...", "token_type": "bearer", "expires_in": 86400 }
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.jwt_handler import create_token, _VALID_API_KEYS, JWT_EXPIRY_HOURS

router = APIRouter()


class TokenRequest(BaseModel):
    tenant_id: str
    api_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


@router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest):
    """
    Exchange a tenant_id + api_key for a signed JWT.

    In production the api_key would be validated against a database.
    In this demo environment any key matching the known list is accepted.
    """
    # Validate api_key belongs to the stated tenant
    expected_tenant = _VALID_API_KEYS.get(body.api_key)
    if expected_tenant is None or expected_tenant != body.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or tenant_id mismatch.",
        )

    token = create_token(body.tenant_id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRY_HOURS * 3600,
    )
