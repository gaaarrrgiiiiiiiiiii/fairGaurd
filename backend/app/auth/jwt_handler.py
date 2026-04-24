"""
JWT authentication utilities.

  verify_token(token)   — validate a Bearer token, return tenant_id or None
  create_token(tenant_id) — generate a signed JWT for a tenant
"""
import datetime
import os
from typing import Optional

import jwt

JWT_SECRET    = os.getenv("JWT_SECRET", "fairguard-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# Simple in-memory API key store for dev/demo.
# In production, these would be fetched from a tenant database.
_VALID_API_KEYS = {
    "sk_fgt_12345":   "tenant_demo",
    "sk_fgt_test":    "tenant_test",
    "sk_test":        "tenant_test",
    "sk_test_123":    "tenant_test",
}


def create_token(tenant_id: str) -> str:
    """Generate a signed JWT for the given tenant."""
    payload = {
        "tenant_id": tenant_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
               + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: Optional[str]) -> Optional[str]:
    """
    Validate a Bearer token and return the tenant_id, or None if invalid.

    Accepts:
      • A full JWT (preferred)
      • A raw API key (sk_fgt_…) for backward compatibility
    """
    if not token:
        return None

    # Strip "Bearer " prefix if present
    raw = token.removeprefix("Bearer ").strip()

    # 1. Try raw API key lookup (simple string match)
    if raw in _VALID_API_KEYS:
        return _VALID_API_KEYS[raw]

    # 2. Try JWT decode
    try:
        decoded = jwt.decode(raw, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded.get("tenant_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
