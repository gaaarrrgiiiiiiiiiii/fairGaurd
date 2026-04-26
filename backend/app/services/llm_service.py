"""
LLM Service — async compliance explanation generation.

C2: Replaced sync `requests` with `httpx.AsyncClient` (non-blocking).
Cascades: Gemini → Groq → Mistral → deterministic template.
"""
import logging
import os
from typing import List

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Shared timeout: 3s total, 1s connect
_TIMEOUT = httpx.Timeout(3.0, connect=1.0)

_SYSTEM_MSG = "You provide extremely concise, professional, legal-sounding compliance logs."


class LLMService:
    async def generate_explanation(
        self,
        features: dict,
        original_decision: str,
        corrected_decision: str,
        protected_attributes: List[str],
    ) -> str:
        """
        C2: Fully async LLM call. Never blocks the event loop.
        Called as a background task (fire-and-forget) by the decisions router.
        """
        prompt = (
            f"You are an AI fairness compliance auditor. "
            f"An ML model originally decided '{original_decision}' for an applicant "
            f"with features {features}. "
            f"A demographic bias was detected on attributes {protected_attributes}. "
            f"The decision was corrected to '{corrected_decision}'. "
            f"Write exactly ONE concise legal sentence for the compliance audit log."
        )

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:

            # 1. Gemini (preferred — Google Solution Challenge alignment)
            if GEMINI_API_KEY:
                try:
                    resp = await client.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/"
                        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "systemInstruction": {"parts": [{"text": _SYSTEM_MSG}]},
                            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 60},
                        },
                    )
                    resp.raise_for_status()
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                except Exception as exc:
                    logger.warning("Gemini LLM failed: %s", exc)

            # 2. Groq — fast LLaMA 3 inference
            if GROQ_API_KEY:
                try:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                        json={
                            "model": "llama3-8b-8192",
                            "messages": [
                                {"role": "system", "content": _SYSTEM_MSG},
                                {"role": "user",   "content": prompt},
                            ],
                            "temperature": 0.2,
                            "max_tokens": 60,
                        },
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"].strip()
                except Exception as exc:
                    logger.warning("Groq LLM failed: %s", exc)

            # 3. Mistral
            if MISTRAL_API_KEY:
                try:
                    resp = await client.post(
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                        json={
                            "model": "mistral-tiny",
                            "messages": [
                                {"role": "system", "content": _SYSTEM_MSG},
                                {"role": "user",   "content": prompt},
                            ],
                            "temperature": 0.2,
                            "max_tokens": 60,
                        },
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"].strip()
                except Exception as exc:
                    logger.warning("Mistral LLM failed: %s", exc)

        # Deterministic template fallback — always EU AI Act compliant
        return (
            f"Decision overridden from '{original_decision}' to '{corrected_decision}' "
            f"following automated bias detection on protected attributes "
            f"{protected_attributes} per EU AI Act Article 13 post-market monitoring."
        )


llm_service = LLMService()
