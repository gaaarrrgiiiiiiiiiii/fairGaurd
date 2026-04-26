"""
JWT authentication utilities.

  verify_token(token)            — validate token, return (tenant_id, role) or None
  create_token(tenant_id, role)  — generate signed JWT with role claim
  get_valid_api_keys()           — load API keys from environment

Environment variables:
  JWT_SECRET           — HS256 signing secret (REQUIRED in prod)
  JWT_EXPIRY_HOURS     — token TTL (default: 24)
  FAIRGUARD_API_KEYS   — JSON object mapping raw API keys to tenant IDs
                         e.g. '{"sk_fgt_abc": "tenant_acme"}'
  FAIRGUARD_API_ROLES  — JSON object mapping raw API keys to roles
                         e.g. '{"sk_fgt_abc": "admin"}'
                         Defaults to 'admin' if key not present.
  FAIRGUARD_DEV_MODE   — if "true", accepts unauthenticated requests in dev
"""
import datetime
import json
import logging
import os
from typing import Dict, Optional

import jwt

logger = logging.getLogger(__name__)

JWT_SECRET       = os.getenv("JWT_SECRET", "fairguard-dev-secret-change-in-prod")
JWT_ALGORITHM    = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
DEV_MODE         = os.getenv("FAIRGUARD_DEV_MODE", "false").lower() == "true"

if JWT_SECRET == "fairguard-dev-secret-change-in-prod" and not DEV_MODE:
    logger.warning(
        "⚠️  JWT_SECRET is using the insecure default value. "
        "Set a strong secret in your .env file before deploying."
    )


def _load_api_keys() -> Dict[str, str]:
    """
    Load API key → tenant_id mapping from the FAIRGUARD_API_KEYS env var.

    Expected format (JSON):
        {"sk_fgt_abc123": "tenant_acme", "sk_fgt_xyz789": "tenant_beta"}

    Returns an empty dict if the env var is absent or malformed.
    """
    raw = os.getenv("FAIRGUARD_API_KEYS", "")
    if not raw:
        if not DEV_MODE:
            logger.warning(
                "FAIRGUARD_API_KEYS is not set. "
                "No raw API key authentication will work. "
                "Set FAIRGUARD_DEV_MODE=true only for local development."
            )
        return {}
    try:
        keys = json.loads(raw)
        if not isinstance(keys, dict):
            raise ValueError("FAIRGUARD_API_KEYS must be a JSON object")
        return {str(k): str(v) for k, v in keys.items()}
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse FAIRGUARD_API_KEYS: %s", exc)
        return {}


# Loaded once at startup — no secrets in source code.
_API_KEYS: Dict[str, str] = _load_api_keys()


def _load_api_roles() -> Dict[str, str]:
    """
    Load API key → role mapping from FAIRGUARD_API_ROLES env var.
    Roles: 'admin' | 'auditor' | 'viewer'
    Defaults to 'admin' if a key is not listed.
    """
    raw = os.getenv("FAIRGUARD_API_ROLES", "")
    if not raw:
        return {}
    try:
        roles = json.loads(raw)
        valid = {"admin", "auditor", "viewer"}
        return {str(k): str(v) if str(v) in valid else "viewer" for k, v in roles.items()}
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse FAIRGUARD_API_ROLES: %s", exc)
        return {}


_API_ROLES: Dict[str, str] = _load_api_roles()


def create_token(tenant_id: str, role: str = "admin") -> str:
    """Generate a signed JWT for the given tenant with a role claim."""
    valid_roles = {"admin", "auditor", "viewer"}
    if role not in valid_roles:
        role = "viewer"
    payload = {
        "tenant_id": tenant_id,
        "role": role,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
               + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: Optional[str]) -> Optional[tuple]:
    """
    Validate a Bearer token and return (tenant_id, role), or None if invalid.

    Accepts:
      • A full JWT (preferred for production)
      • A raw API key matching FAIRGUARD_API_KEYS (for SDK/curl usage)

    Role defaults to 'admin' for backward-compatible tokens without role claim.
    """
    if not token:
        return None

    raw = token.removeprefix("Bearer ").strip()

    # 1. Raw API key lookup
    if raw in _API_KEYS:
        tenant_id = _API_KEYS[raw]
        role = _API_ROLES.get(raw, "admin")
        return (tenant_id, role)

    # 2. JWT decode
    try:
        decoded = jwt.decode(raw, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        tenant_id = decoded.get("tenant_id")
        role = decoded.get("role", "admin")  # backward compat
        if tenant_id:
            return (tenant_id, role)
        return None
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid token")
        return None
