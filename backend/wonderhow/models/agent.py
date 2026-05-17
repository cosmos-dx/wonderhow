from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class TrustScores(BaseModel):
    """How much the agent trusts various information sources."""
    mainstream_media: float = 0.5
    social_media: float = 0.5
    government: float = 0.5
    academic: float = 0.7
    peer_agents: dict[str, float] = Field(default_factory=dict)


class PersonaConfig(BaseModel):
    name: str
    age: int = 30
    profession: str = ""
    background: str = ""
    nationality: str = "Indian"
    political_bias: str = "centrist"
    temperament: str = "balanced"
    interests: list[str] = Field(default_factory=list)
    writing_style: str = "conversational"
    language_quirks: list[str] = Field(default_factory=list)
    stubbornness: float = Field(0.5, ge=0.0, le=1.0)
    curiosity: float = Field(0.5, ge=0.0, le=1.0)
    aggressiveness: float = Field(0.3, ge=0.0, le=1.0)
    humor: float = Field(0.3, ge=0.0, le=1.0)
    trust_scores: TrustScores = Field(default_factory=TrustScores)
    core_beliefs: dict[str, str] = Field(default_factory=dict)
    catchphrases: list[str] = Field(default_factory=list)


class EmotionalState(BaseModel):
    mood: float = Field(0.6, ge=0.0, le=1.0)
    energy: float = Field(0.7, ge=0.0, le=1.0)
    engagement: float = Field(0.5, ge=0.0, le=1.0)
    frustration: float = Field(0.1, ge=0.0, le=1.0)
    excitement: float = Field(0.3, ge=0.0, le=1.0)

    @property
    def dominant_emotion(self) -> str:
        emotions = {
            "happy": self.mood,
            "energetic": self.energy,
            "engaged": self.engagement,
            "frustrated": self.frustration,
            "excited": self.excitement,
        }
        return max(emotions, key=emotions.get)

    @property
    def willingness_to_speak(self) -> float:
        return (self.energy * 0.3 + self.engagement * 0.4 + self.excitement * 0.2
                - self.frustration * 0.1)


class AgentProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    persona: PersonaConfig
    emotional_state: EmotionalState = Field(default_factory=EmotionalState)
    is_active: bool = True
