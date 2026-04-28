"""
Auth router — user registration, login, and JWT token issuance.

POST /v1/auth/register   — create a new user account (name, email, org, role, password)
POST /v1/auth/login      — authenticate with email + password → JWT token
POST /v1/auth/token      — legacy: exchange api_key for JWT (backward compat)
GET  /v1/auth/me         — return current user profile (requires Bearer token)
"""
import datetime
import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.auth.jwt_handler import (
    JWT_EXPIRY_HOURS,
    _load_api_keys,
    create_token,
    verify_token,
)
from app.models.database import SessionLocal, User, get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    """Simple SHA-256 hash for demo — swap for bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


def _check_password(password: str, stored_hash: str) -> bool:
    return _hash_password(password) == stored_hash


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str         = Field(..., min_length=1, max_length=128)
    email: str        = Field(..., min_length=3, max_length=256)
    organization: str = Field("", max_length=256)
    role: str         = Field("analyst", max_length=64)
    password: str     = Field(..., min_length=6, max_length=256)


class LoginRequest(BaseModel):
    email: str    = Field(..., min_length=3, max_length=256)
    password: str = Field(..., min_length=1, max_length=256)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    organization: Optional[str]
    role: str
    tenant_id: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRequest(BaseModel):
    tenant_id: str = Field(..., min_length=1, max_length=128)
    api_key: str   = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new FairGuard user account.
    Returns a JWT token so the frontend can navigate straight to the dashboard.
    """
    # Check for duplicate email
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Derive a tenant_id from the organisation (slug-style)
    org_slug = (body.organization or body.email.split("@")[-1]).lower().replace(" ", "_")
    tenant_id = f"tenant_{org_slug}"

    user = User(
        email=body.email,
        name=body.name,
        organization=body.organization or None,
        role=body.role,
        tenant_id=tenant_id,
        password_hash=_hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.tenant_id, user.role)
    logger.info("New user registered: %s (tenant=%s)", user.email, tenant_id)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        organization=user.organization,
        role=user.role,
        tenant_id=user.tenant_id,
        access_token=token,
        expires_in=JWT_EXPIRY_HOURS * 3600,
    )


@router.post("/login", response_model=UserResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email + password, return a fresh JWT."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not _check_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    # Update last login
    user.last_login_at = datetime.datetime.utcnow()
    db.commit()

    token = create_token(user.tenant_id, user.role)
    logger.info("User logged in: %s", user.email)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        organization=user.organization,
        role=user.role,
        tenant_id=user.tenant_id,
        access_token=token,
        expires_in=JWT_EXPIRY_HOURS * 3600,
    )


@router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest):
    """
    Legacy endpoint — exchange a tenant_id + api_key for a signed JWT.
    API keys are validated against FAIRGUARD_API_KEYS environment variable.
    """
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
