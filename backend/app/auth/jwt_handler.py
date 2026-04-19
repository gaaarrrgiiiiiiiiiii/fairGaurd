import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

def verify_token(token: str) -> str:
    try:
        # Strip Bearer if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded.get("tenant_id", "tenant_default")
    except Exception:
        return None
