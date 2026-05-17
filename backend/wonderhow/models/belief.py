from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class Belief(BaseModel):
    topic: str
    stance: str
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    source_weights: dict[str, float] = Field(default_factory=dict)
    times_challenged: int = 0
    last_challenged_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def challenge(self, counter_evidence: str, counter_confidence: float) -> bool:
        """Returns True if the belief was updated/weakened."""
        self.times_challenged += 1
        self.last_challenged_at = datetime.utcnow()

        impact = counter_confidence * (1 - self.confidence * 0.5)
        if impact > 0.3:
            self.confidence = max(0.05, self.confidence - impact * 0.15)
            self.evidence.append(f"[challenged] {counter_evidence}")
            self.updated_at = datetime.utcnow()
            return True
        return False

    def reinforce(self, supporting_evidence: str, strength: float = 0.1):
        self.confidence = min(0.99, self.confidence + strength)
        self.evidence.append(f"[supported] {supporting_evidence}")
        self.updated_at = datetime.utcnow()


class BeliefSystem(BaseModel):
    beliefs: dict[str, Belief] = Field(default_factory=dict)

    def get_belief(self, topic: str) -> Belief | None:
        normalized = topic.lower().strip()
        for key, belief in self.beliefs.items():
            if normalized in key.lower() or key.lower() in normalized:
                return belief
        return None

    def set_belief(self, topic: str, stance: str, confidence: float = 0.5,
                   evidence: list[str] | None = None):
        self.beliefs[topic] = Belief(
            topic=topic, stance=stance, confidence=confidence,
            evidence=evidence or [],
        )

    def topics(self) -> list[str]:
        return list(self.beliefs.keys())
