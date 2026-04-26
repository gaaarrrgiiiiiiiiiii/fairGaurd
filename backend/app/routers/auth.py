"""
Auth router — issue JWT tokens for tenants.

POST /v1/auth/token
  Body: { "tenant_id": "...", "api_key": "sk_fgt_..." }
  Response: { "access_token": "eyJ...", "token_type": "bearer", "expires_in": 86400 }

API keys are loaded from FAIRGUARD_API_KEYS env var — never hardcoded.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.jwt_handler import create_token, verify_token, JWT_EXPIRY_HOURS, _load_api_keys

router = APIRouter()


class TokenRequest(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=128)
    api_key: str   = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


@router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest):
    """
    Exchange a tenant_id + api_key for a signed JWT.

    API keys are validated against FAIRGUARD_API_KEYS environment variable.
    Returns 401 on any mismatch — no timing oracle leakage.
    """
    # Reload keys each call so key rotation takes effect without restart.
    # In a high-traffic prod system this would be cached with a TTL.
    api_keys = _load_api_keys()

    expected_tenant = api_keys.get(body.api_key)
    if expected_tenant is None or expected_tenant != body.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key or tenant_id mismatch.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_token(body.tenant_id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRY_HOURS * 3600,
    )
