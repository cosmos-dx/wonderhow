from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    agent_id: str
    agent_name: str = ""
    content: str
    message_type: str = "chat"
    emotional_tone: str = "neutral"
    sources: list[str] = Field(default_factory=list)
    reply_to: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
