"""
Upgraded FairGuard Python SDK — Phase 3A (Gap 10)

Improvements over v1:
  • httpx for both sync and async support
  • Exponential back-off retries (max 3 attempts) using tenacity
  • Async variant: FairGuardAsyncClient
  • evaluate_batch() that calls POST /v1/decisions/batch
  • Typed custom exceptions
  • Domain support — pass domain="healthcare" etc.

Install:
    pip install fairguard-sdk
    # or from source: pip install -e sdk/

Quickstart:
    from fairguard_sdk import FairGuardClient
    client = FairGuardClient(api_key="sk_fgt_...")
    result = client.evaluate(
        applicant_features={"age": 35, "income": 55000, "sex": "Female"},
        model_output={"decision": "denied", "confidence": 0.73},
        protected_attributes=["sex"],
        domain="lending",
    )
"""
from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------
class FairGuardError(Exception):
    """Base exception for all SDK errors."""

class FairGuardAuthError(FairGuardError):
    """Raised on 401/403 responses."""

class FairGuardValidationError(FairGuardError):
    """Raised on 422 validation errors from the API."""

class FairGuardRateLimitError(FairGuardError):
    """Raised when the API returns 429 Too Many Requests."""

class FairGuardServerError(FairGuardError):
    """Raised on 5xx server errors."""


# ---------------------------------------------------------------------------
# Internal helper: raise typed exceptions from HTTP status
# ---------------------------------------------------------------------------
def _raise_for_status(status_code: int, body: Any) -> None:
    if status_code == 401 or status_code == 403:
        raise FairGuardAuthError(f"HTTP {status_code}: {body}")
    if status_code == 422:
        raise FairGuardValidationError(f"Validation error: {body}")
    if status_code == 429:
        raise FairGuardRateLimitError("Rate limit exceeded. Back off and retry.")
    if status_code >= 500:
        raise FairGuardServerError(f"Server error {status_code}: {body}")
    if status_code >= 400:
        raise FairGuardError(f"HTTP {status_code}: {body}")


# ---------------------------------------------------------------------------
# Sync Client
# ---------------------------------------------------------------------------
class FairGuardClient:
    """
    Synchronous FairGuard client with automatic retries.

    Args:
        api_key:  Your FairGuard API key (or set FAIRGUARD_API_KEY env var).
        base_url: API base URL (default: http://localhost:8000).
        timeout:  Request timeout in seconds (default: 30).
        max_retries: Max retry attempts on transient failures (default: 3).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or os.environ.get("FAIRGUARD_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict) -> dict:
        """POST with exponential back-off retry."""
        try:
            import httpx
        except ImportError:
            raise FairGuardError("httpx is required: pip install httpx")

        last_exc: Exception = RuntimeError("No attempts made")
        wait = 1.0
        for attempt in range(1, self.max_retries + 1):
            try:
                r = httpx.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=self._headers,
                    timeout=self.timeout,
                )
                body = r.json() if r.content else {}
                _raise_for_status(r.status_code, body)
                return body
            except (FairGuardRateLimitError, FairGuardServerError) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    import time
                    logger.warning("Retry %d/%d after %.1fs — %s", attempt, self.max_retries, wait, exc)
                    time.sleep(wait)
                    wait = min(wait * 2, 30.0)
            except FairGuardError:
                raise  # non-retriable
        raise last_exc

    def evaluate(
        self,
        applicant_features: Dict[str, Any],
        model_output: Dict[str, Any],
        protected_attributes: List[str],
        domain: str = "lending",
        mode: str = "detect_and_correct",
    ) -> dict:
        """
        Evaluate a single decision for bias.

        Returns the full FairGuard response including:
          corrected_decision, bias_scores, causal_paths, explanation.
        """
        return self._post("/v1/decision", {
            "applicant_features": applicant_features,
            "model_output": model_output,
            "protected_attributes": protected_attributes,
            "domain": domain,
            "mode": mode,
        })

    def evaluate_batch(
        self,
        decisions: List[Dict[str, Any]],
    ) -> dict:
        """
        Evaluate a batch of decisions concurrently (max 100 per call).

        Each item in decisions should be a dict matching the single-evaluate
        signature: {applicant_features, model_output, protected_attributes,
        domain?, mode?}
        """
        return self._post("/v1/decisions/batch", {"decisions": decisions})

    def get_analytics(self) -> dict:
        """Fetch real-time compliance analytics for your tenant."""
        try:
            import httpx
        except ImportError:
            raise FairGuardError("httpx is required: pip install httpx")
        r = httpx.get(
            f"{self.base_url}/v1/report/analytics",
            headers=self._headers,
            timeout=self.timeout,
        )
        body = r.json() if r.content else {}
        _raise_for_status(r.status_code, body)
        return body

    def download_compliance_report(self, dest_path: str = "fairguard_report.pdf") -> str:
        """Download the EU AI Act compliance PDF and save to disk."""
        try:
            import httpx
        except ImportError:
            raise FairGuardError("httpx is required: pip install httpx")
        r = httpx.get(
            f"{self.base_url}/v1/report/generate",
            headers=self._headers,
            timeout=60.0,
        )
        _raise_for_status(r.status_code, {})
        with open(dest_path, "wb") as f:
            f.write(r.content)
        return dest_path


# ---------------------------------------------------------------------------
# Async Client
# ---------------------------------------------------------------------------
class FairGuardAsyncClient:
    """
    Async FairGuard client using httpx.AsyncClient.

    Use with `async with FairGuardAsyncClient(...) as client: ...`
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("FAIRGUARD_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self._client = None

    async def __aenter__(self):
        try:
            import httpx
        except ImportError:
            raise FairGuardError("httpx is required: pip install httpx")
        self._client = httpx.AsyncClient(headers=self._headers, timeout=self.timeout)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def evaluate_async(
        self,
        applicant_features: Dict[str, Any],
        model_output: Dict[str, Any],
        protected_attributes: List[str],
        domain: str = "lending",
        mode: str = "detect_and_correct",
    ) -> dict:
        """Async single-decision evaluation."""
        r = await self._client.post(
            f"{self.base_url}/v1/decision",
            json={
                "applicant_features": applicant_features,
                "model_output": model_output,
                "protected_attributes": protected_attributes,
                "domain": domain,
                "mode": mode,
            },
        )
        body = r.json() if r.content else {}
        _raise_for_status(r.status_code, body)
        return body

    async def evaluate_batch_async(self, decisions: List[Dict[str, Any]]) -> dict:
        """Async batch evaluation."""
        r = await self._client.post(
            f"{self.base_url}/v1/decisions/batch",
            json={"decisions": decisions},
        )
        body = r.json() if r.content else {}
        _raise_for_status(r.status_code, body)
        return body


# ---------------------------------------------------------------------------
# Example / quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    _key = os.environ.get("FAIRGUARD_API_KEY", "")
    if not _key:
        raise RuntimeError("Set FAIRGUARD_API_KEY before running.")

    client = FairGuardClient(api_key=_key)

    result = client.evaluate(
        applicant_features={"age": 35, "income": 55000, "sex": "Female"},
        model_output={"decision": "denied", "confidence": 0.73},
        protected_attributes=["sex"],
        domain="lending",
    )
    print(json.dumps(result, indent=2))
