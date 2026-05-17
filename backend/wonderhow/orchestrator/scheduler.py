from __future__ import annotations

import random
import logging
from wonderhow.engine.agent_engine import AgentEngine

logger = logging.getLogger(__name__)


class AgentScheduler:
    """Decides which agents act in each tick, weighted by energy/relevance."""

    def select_agents(
        self,
        agents: list[AgentEngine],
        topic: str,
        max_active: int = 3,
    ) -> list[AgentEngine]:
        if not agents:
            return []

        scored: list[tuple[AgentEngine, float]] = []
        for agent in agents:
            if not agent.profile.is_active:
                continue
            score = self._compute_priority(agent, topic)
            scored.append((agent, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        n = min(max_active, len(scored))
        if n <= 0:
            return []

        top = scored[:n]
        selected = []
        for agent, score in top:
            if random.random() < min(score, 0.95):
                selected.append(agent)

        if not selected and scored:
            selected.append(scored[0][0])

        return selected

    def _compute_priority(self, agent: AgentEngine, topic: str) -> float:
        es = agent.emotional_state
        persona = agent.persona

        topic_relevance = 0.3
        topic_lower = topic.lower()
        for interest in persona.interests:
            if interest.lower() in topic_lower or topic_lower in interest.lower():
                topic_relevance = 0.9
                break

        time_factor = min(1.0, agent.time_since_last_spoke() / 120.0)
        energy_factor = es.energy * 0.3
        engagement_factor = es.engagement * 0.3

        score = (
            topic_relevance * 0.35
            + time_factor * 0.25
            + energy_factor * 0.2
            + engagement_factor * 0.2
        )

        return score
