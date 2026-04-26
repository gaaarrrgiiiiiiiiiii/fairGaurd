"""
JWT authentication utilities.

  verify_token(token)    — validate a Bearer token, return tenant_id or None
  create_token(tenant_id) — generate a signed JWT for a tenant
  get_valid_api_keys()   — load API keys from environment (never hardcoded)

Environment variables:
  JWT_SECRET           — HS256 signing secret (REQUIRED in prod)
  JWT_EXPIRY_HOURS     — token TTL (default: 24)
  FAIRGUARD_API_KEYS   — JSON object mapping raw API keys to tenant IDs
                         e.g. '{"sk_fgt_abc": "tenant_acme"}'
  FAIRGUARD_DEV_MODE   — if "true", a synthetic dev tenant is accepted when
                         no valid token is provided (NEVER enable in prod)
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
      • A full JWT (preferred for production)
      • A raw API key matching FAIRGUARD_API_KEYS (for SDK/curl usage)
    """
    if not token:
        return None

    raw = token.removeprefix("Bearer ").strip()

    # 1. Raw API key lookup (loaded from env — no hardcoded secrets)
    if raw in _API_KEYS:
        return _API_KEYS[raw]

    # 2. JWT decode
    try:
        decoded = jwt.decode(raw, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded.get("tenant_id")
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid token")
        return None
