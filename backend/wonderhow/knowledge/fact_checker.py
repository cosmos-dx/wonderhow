from __future__ import annotations

import json
import logging
from openai import AsyncOpenAI

from wonderhow.config import settings
from wonderhow.prompts.moderation_prompts import FACT_CHECK_PROMPT

logger = logging.getLogger(__name__)


class FactChecker:
    """LLM-based fact checking with optional web verification."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def check_claim(self, claim: str, context: str = "") -> dict:
        prompt = f"Claim: {claim}"
        if context:
            prompt += f"\nContext: {context}"

        try:
            response = await self._client.chat.completions.create(
                model=settings.openai_model_fast,
                messages=[
                    {"role": "system", "content": FACT_CHECK_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception:
            logger.warning("Fact check failed for claim: %s", claim[:80], exc_info=True)
            return {
                "claim": claim,
                "verdict": "unverifiable",
                "confidence": 0.0,
                "explanation": "Fact check unavailable",
            }

    async def moderate_message(self, message: str, agent_name: str) -> dict:
        from wonderhow.prompts.moderation_prompts import (
            MODERATION_SYSTEM_PROMPT, build_moderation_check,
        )
        try:
            response = await self._client.chat.completions.create(
                model=settings.openai_model_fast,
                messages=[
                    {"role": "system", "content": MODERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": build_moderation_check(message, agent_name)},
                ],
                max_tokens=150,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception:
            logger.warning("Moderation check failed", exc_info=True)
            return {"safe": True, "reason": "", "severity": "none"}
