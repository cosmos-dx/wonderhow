import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Float, DateTime, JSON, Boolean, Integer, func,
)
from sqlalchemy.dialects.postgresql import UUID

from wonderhow.db.database import Base


def new_uuid():
    return uuid.uuid4()


class EpisodicMemoryRow(Base):
    __tablename__ = "episodic_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    agent_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    emotional_impact = Column(Float, default=0.0)
    importance = Column(Float, default=0.5)
    created_at = Column(DateTime, server_default=func.now())
