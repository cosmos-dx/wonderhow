from __future__ import annotations

import random
from wonderhow.models.agent import EmotionalState


def decay_toward_baseline(value: float, baseline: float, rate: float = 0.05) -> float:
    diff = baseline - value
    return value + diff * rate


def update_emotion_from_interaction(
    state: EmotionalState,
    interaction_type: str,
    intensity: float = 0.5,
) -> EmotionalState:
    """Update emotional state based on what happened in a conversation turn.

    interaction_type: 'agreement', 'disagreement', 'attack', 'support',
                      'new_topic', 'idle', 'fact_challenged', 'won_argument'
    """
    jitter = random.uniform(-0.05, 0.05)

    if interaction_type == "agreement":
        state.mood = min(1.0, state.mood + 0.08 * intensity + jitter)
        state.frustration = max(0.0, state.frustration - 0.05)
        state.engagement = min(1.0, state.engagement + 0.05)
    elif interaction_type == "disagreement":
        state.frustration = min(1.0, state.frustration + 0.1 * intensity + jitter)
        state.engagement = min(1.0, state.engagement + 0.1)
        state.energy = max(0.0, state.energy - 0.03)
    elif interaction_type == "attack":
        state.frustration = min(1.0, state.frustration + 0.2 * intensity)
        state.mood = max(0.0, state.mood - 0.15 * intensity)
        state.engagement = min(1.0, state.engagement + 0.15)
        state.excitement = min(1.0, state.excitement + 0.1)
    elif interaction_type == "support":
        state.mood = min(1.0, state.mood + 0.12 * intensity)
        state.energy = min(1.0, state.energy + 0.05)
        state.frustration = max(0.0, state.frustration - 0.08)
    elif interaction_type == "new_topic":
        state.excitement = min(1.0, state.excitement + 0.15 * intensity + jitter)
        state.engagement = min(1.0, state.engagement + 0.1)
        state.energy = min(1.0, state.energy + 0.05)
    elif interaction_type == "idle":
        state.energy = min(1.0, state.energy + 0.03)
        state.engagement = max(0.0, state.engagement - 0.08)
        state.excitement = max(0.0, state.excitement - 0.05)
        state.frustration = max(0.0, state.frustration - 0.03)
    elif interaction_type == "fact_challenged":
        state.frustration = min(1.0, state.frustration + 0.12 * intensity)
        state.engagement = min(1.0, state.engagement + 0.12)
    elif interaction_type == "won_argument":
        state.mood = min(1.0, state.mood + 0.15)
        state.excitement = min(1.0, state.excitement + 0.1)
        state.energy = min(1.0, state.energy + 0.08)
        state.frustration = max(0.0, state.frustration - 0.1)

    return state


def natural_decay(state: EmotionalState) -> EmotionalState:
    """Over time, emotions drift back toward baseline."""
    state.mood = decay_toward_baseline(state.mood, 0.6)
    state.energy = decay_toward_baseline(state.energy, 0.7)
    state.engagement = decay_toward_baseline(state.engagement, 0.5)
    state.frustration = decay_toward_baseline(state.frustration, 0.1)
    state.excitement = decay_toward_baseline(state.excitement, 0.3)
    return state


def emotion_summary(state: EmotionalState) -> str:
    parts = []
    if state.frustration > 0.6:
        parts.append("frustrated and heated")
    elif state.frustration > 0.3:
        parts.append("slightly irritated")
    if state.excitement > 0.7:
        parts.append("very excited")
    elif state.excitement > 0.4:
        parts.append("interested")
    if state.mood > 0.7:
        parts.append("in a good mood")
    elif state.mood < 0.3:
        parts.append("in a bad mood")
    if state.energy < 0.3:
        parts.append("low energy")
    if state.engagement > 0.7:
        parts.append("deeply engaged")
    elif state.engagement < 0.3:
        parts.append("disengaged and bored")
    return ", ".join(parts) if parts else "calm and neutral"
