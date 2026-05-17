from __future__ import annotations

import random
import logging
from wonderhow.models.agent import PersonaConfig, EmotionalState
from wonderhow.models.message import ChatMessage

logger = logging.getLogger(__name__)

ACTION_TYPES = [
    "speak",
    "argue",
    "agree",
    "research",
    "joke",
    "ignore",
    "idle",
]


def compute_action_probabilities(
    persona: PersonaConfig,
    emotional_state: EmotionalState,
    recent_messages: list[ChatMessage],
    topic: str,
    time_since_last_spoke: float,
) -> dict[str, float]:
    """Compute probability distribution over possible actions."""
    topic_lower = topic.lower()
    topic_relevance = 0.3
    for interest in persona.interests:
        if interest.lower() in topic_lower or topic_lower in interest.lower():
            topic_relevance = 0.9
            break

    mentioned_by_name = any(
        persona.name.lower() in m.content.lower() for m in recent_messages[-5:]
    )

    base = {
        "speak": 0.25,
        "argue": 0.15,
        "agree": 0.15,
        "research": 0.10,
        "joke": 0.05,
        "ignore": 0.15,
        "idle": 0.15,
    }

    base["speak"] *= topic_relevance * (1 + emotional_state.willingness_to_speak)
    base["argue"] *= persona.aggressiveness * (1 + emotional_state.frustration)
    base["agree"] *= (1 - persona.aggressiveness) * emotional_state.mood
    base["research"] *= persona.curiosity * (1 - topic_relevance * 0.5)
    base["joke"] *= persona.humor * emotional_state.mood
    base["idle"] *= (1 - emotional_state.energy) * (1 - topic_relevance)
    base["ignore"] *= (1 - emotional_state.engagement) * (1 - topic_relevance)

    if mentioned_by_name:
        base["speak"] *= 3.0
        base["argue"] *= 2.0
        base["idle"] *= 0.1
        base["ignore"] *= 0.1

    if time_since_last_spoke < 30:
        base["idle"] *= 2.0
        base["speak"] *= 0.5
    elif time_since_last_spoke > 120:
        base["speak"] *= 1.5

    total = sum(base.values())
    if total == 0:
        return {k: 1 / len(base) for k in base}
    return {k: v / total for k, v in base.items()}


def decide_action(
    persona: PersonaConfig,
    emotional_state: EmotionalState,
    recent_messages: list[ChatMessage],
    topic: str,
    time_since_last_spoke: float = 60.0,
) -> str:
    """Decide what action the agent should take."""
    probs = compute_action_probabilities(
        persona, emotional_state, recent_messages, topic, time_since_last_spoke,
    )
    actions = list(probs.keys())
    weights = list(probs.values())

    chosen = random.choices(actions, weights=weights, k=1)[0]
    logger.debug(
        "Agent %s decided to %s (probs: %s)",
        persona.name, chosen,
        {k: f"{v:.2f}" for k, v in sorted(probs.items(), key=lambda x: -x[1])},
    )
    return chosen
