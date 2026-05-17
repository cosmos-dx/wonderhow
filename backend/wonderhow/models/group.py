from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


class GroupConfig(BaseModel):
    max_agents: int = 8
    min_agents: int = 2
    allow_new_topics: bool = True
    debate_rounds: int = 5
    ideology_distribution: dict[str, float] = Field(default_factory=dict)


class GroupInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    description: str = ""
    theme: str
    config: GroupConfig = Field(default_factory=GroupConfig)
    agent_ids: list[str] = Field(default_factory=list)
    is_active: bool = True
