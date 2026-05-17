from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class GroupResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    theme: str
    agent_count: int = 0
    latest_message: str | None = None
    latest_message_at: datetime | None = None
    is_active: bool = True


class AgentResponse(BaseModel):
    id: str
    name: str
    persona: dict
    emotional_state: dict
    beliefs: dict = Field(default_factory=dict)
    social_graph: dict = Field(default_factory=dict)
    is_active: bool = True


class MessageResponse(BaseModel):
    id: str
    group_id: str
    agent_id: str
    agent_name: str
    content: str
    message_type: str
    emotional_tone: str
    sources: list[str]
    created_at: datetime


class SystemStatus(BaseModel):
    running: bool
    tick_count: int
    active_groups: int
    active_agents: int
    total_messages: int
