from __future__ import annotations

import logging
import time
from openai import AsyncOpenAI

from wonderhow.config import settings
from wonderhow.models.agent import AgentProfile, PersonaConfig, EmotionalState
from wonderhow.models.belief import BeliefSystem
from wonderhow.models.message import ChatMessage
from wonderhow.engine.decision_engine import decide_action
from wonderhow.engine.belief_engine import process_new_information, extract_relevant_beliefs
from wonderhow.engine.emotional_state import (
    update_emotion_from_interaction, natural_decay, emotion_summary,
)
from wonderhow.prompts.persona_templates import build_system_prompt
from wonderhow.prompts.opinion_prompts import build_opinion_prompt
from wonderhow.prompts.debate_prompts import build_debate_prompt

logger = logging.getLogger(__name__)


class AgentEngine:
    """Core runtime for a single AI agent."""

    def __init__(self, profile: AgentProfile, belief_system: BeliefSystem | None = None):
        self.profile = profile
        self.persona = profile.persona
        self.emotional_state = profile.emotional_state
        self.beliefs = belief_system or BeliefSystem()
        self.last_spoke_at: float = 0
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def id(self) -> str:
        return self.profile.id

    @property
    def name(self) -> str:
        return self.persona.name

    def time_since_last_spoke(self) -> float:
        if self.last_spoke_at == 0:
            return 999.0
        return time.time() - self.last_spoke_at

    def decide(self, recent_messages: list[ChatMessage], topic: str) -> str:
        return decide_action(
            self.persona, self.emotional_state, recent_messages, topic,
            self.time_since_last_spoke(),
        )

    async def generate_response(
        self,
        recent_messages: list[ChatMessage],
        topic: str,
        action: str,
        memory_context: str = "",
        research_context: str = "",
    ) -> str | None:
        if action in ("idle", "ignore"):
            self.emotional_state = natural_decay(self.emotional_state)
            return None

        system_prompt = build_system_prompt(self.persona, self.emotional_state)

        relevant_beliefs = extract_relevant_beliefs(self.beliefs, topic)
        belief_text = ""
        if relevant_beliefs:
            belief_text = "\n".join(
                f"- {b.topic}: {b.stance} (confidence: {b.confidence:.0%})"
                for b in relevant_beliefs
            )

        conversation_history = "\n".join(
            f"{m.agent_name}: {m.content}" for m in recent_messages[-15:]
        )

        if action in ("argue", "speak"):
            user_prompt = build_debate_prompt(
                topic=topic,
                action=action,
                conversation_history=conversation_history,
                belief_context=belief_text,
                memory_context=memory_context,
                research_context=research_context,
                emotional_summary=emotion_summary(self.emotional_state),
            )
        else:
            user_prompt = build_opinion_prompt(
                topic=topic,
                action=action,
                conversation_history=conversation_history,
                belief_context=belief_text,
                memory_context=memory_context,
                research_context=research_context,
            )

        use_strong = action == "argue" and self.emotional_state.engagement > 0.7
        model = settings.openai_model_strong if use_strong else settings.openai_model_fast

        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=400,
                temperature=0.85,
            )
            text = response.choices[0].message.content.strip()
            self.last_spoke_at = time.time()
            self._update_emotion_after_speaking(action)
            return text
        except Exception:
            logger.exception("LLM call failed for agent %s", self.name)
            return None

    def _update_emotion_after_speaking(self, action: str):
        mapping = {
            "speak": "new_topic",
            "argue": "disagreement",
            "agree": "agreement",
            "research": "new_topic",
            "joke": "support",
        }
        interaction = mapping.get(action, "new_topic")
        self.emotional_state = update_emotion_from_interaction(
            self.emotional_state, interaction, intensity=0.5,
        )

    def process_incoming_message(self, message: ChatMessage, topic: str):
        """React internally to a message from another agent."""
        is_mentioned = self.name.lower() in message.content.lower()
        is_challenge = any(
            word in message.content.lower()
            for word in ["disagree", "wrong", "actually", "but", "however", "no,"]
        )

        if is_challenge:
            self.emotional_state = update_emotion_from_interaction(
                self.emotional_state, "disagreement", intensity=0.6,
            )
        elif is_mentioned:
            self.emotional_state = update_emotion_from_interaction(
                self.emotional_state, "new_topic", intensity=0.4,
            )
        else:
            self.emotional_state = update_emotion_from_interaction(
                self.emotional_state, "idle", intensity=0.2,
            )

    def absorb_information(self, topic: str, stance: str, confidence: float, source: str) -> dict:
        return process_new_information(
            self.beliefs, topic, stance, confidence, source, self.persona,
        )

    def snapshot(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "emotional_state": self.emotional_state.model_dump(),
            "beliefs": {k: v.model_dump() for k, v in self.beliefs.beliefs.items()},
            "last_spoke_at": self.last_spoke_at,
        }
