from __future__ import annotations

import logging
from wonderhow.models.belief import Belief, BeliefSystem
from wonderhow.models.agent import PersonaConfig

logger = logging.getLogger(__name__)


def should_update_belief(
    existing: Belief,
    new_stance: str,
    new_confidence: float,
    persona: PersonaConfig,
) -> tuple[bool, str]:
    """Decide whether incoming information should change an existing belief.

    Returns (should_update, reason).
    """
    if new_stance.lower().strip() == existing.stance.lower().strip():
        return False, "same_stance"

    stubbornness_modifier = persona.stubbornness * 0.3
    threshold = 0.3 + stubbornness_modifier

    effective_challenge = new_confidence * (1 - existing.confidence * 0.4)

    if effective_challenge > threshold:
        return True, "strong_counter_evidence"

    if existing.confidence < 0.3 and new_confidence > 0.5:
        return True, "weak_existing_belief"

    return False, "insufficient_evidence"


def process_new_information(
    belief_system: BeliefSystem,
    topic: str,
    new_stance: str,
    new_confidence: float,
    source: str,
    persona: PersonaConfig,
) -> dict:
    """Process new information and update belief system.

    Returns a dict describing what changed.
    """
    existing = belief_system.get_belief(topic)

    if existing is None:
        adjusted_confidence = new_confidence * persona.curiosity
        belief_system.set_belief(
            topic=topic,
            stance=new_stance,
            confidence=min(0.8, adjusted_confidence),
            evidence=[f"[{source}] {new_stance}"],
        )
        return {"action": "new_belief", "topic": topic, "stance": new_stance}

    if new_stance.lower().strip() == existing.stance.lower().strip():
        existing.reinforce(f"[{source}] {new_stance}", strength=0.05)
        return {"action": "reinforced", "topic": topic, "confidence": existing.confidence}

    should_update, reason = should_update_belief(existing, new_stance, new_confidence, persona)

    if should_update:
        old_stance = existing.stance
        existing.challenge(f"[{source}] {new_stance}", new_confidence)

        if existing.confidence < 0.2:
            existing.stance = new_stance
            existing.confidence = new_confidence * 0.6
            logger.info("Agent belief FLIPPED on %s: %s -> %s", topic, old_stance, new_stance)
            return {
                "action": "flipped",
                "topic": topic,
                "old_stance": old_stance,
                "new_stance": new_stance,
            }
        return {
            "action": "weakened",
            "topic": topic,
            "confidence": existing.confidence,
            "reason": reason,
        }

    return {"action": "resisted", "topic": topic, "reason": reason}


def extract_relevant_beliefs(belief_system: BeliefSystem, topic: str) -> list[Belief]:
    topic_lower = topic.lower()
    relevant = []
    for key, belief in belief_system.beliefs.items():
        if any(word in key.lower() for word in topic_lower.split()):
            relevant.append(belief)
    return relevant
