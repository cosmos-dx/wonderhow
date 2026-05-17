from __future__ import annotations

import uuid
import logging
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from wonderhow.db.tables import EpisodicMemoryRow
from wonderhow.db.database import async_session

logger = logging.getLogger(__name__)


class EpisodicMemory:
    """PostgreSQL-backed event memory for individual agents."""

    async def store(
        self,
        agent_id: str,
        event_type: str,
        summary: str,
        details: dict | None = None,
        emotional_impact: float = 0.0,
        importance: float = 0.5,
    ):
        try:
            async with async_session() as session:
                row = EpisodicMemoryRow(
                    id=uuid.uuid4(),
                    agent_id=uuid.UUID(agent_id),
                    event_type=event_type,
                    summary=summary,
                    details=details or {},
                    emotional_impact=emotional_impact,
                    importance=importance,
                )
                session.add(row)
                await session.commit()
        except Exception:
            logger.warning("Failed to store episodic memory for %s", agent_id, exc_info=True)

    async def recall(
        self, agent_id: str, limit: int = 10, min_importance: float = 0.3
    ) -> list[dict]:
        try:
            async with async_session() as session:
                stmt = (
                    select(EpisodicMemoryRow)
                    .where(
                        EpisodicMemoryRow.agent_id == uuid.UUID(agent_id),
                        EpisodicMemoryRow.importance >= min_importance,
                    )
                    .order_by(desc(EpisodicMemoryRow.created_at))
                    .limit(limit)
                )
                result = await session.execute(stmt)
                rows = result.scalars().all()
                return [
                    {
                        "event_type": r.event_type,
                        "summary": r.summary,
                        "emotional_impact": r.emotional_impact,
                        "importance": r.importance,
                        "when": r.created_at.isoformat() if r.created_at else "",
                    }
                    for r in rows
                ]
        except Exception:
            logger.warning("Failed to recall episodic memories for %s", agent_id, exc_info=True)
            return []

    async def recall_about(self, agent_id: str, keyword: str, limit: int = 5) -> list[dict]:
        try:
            async with async_session() as session:
                stmt = (
                    select(EpisodicMemoryRow)
                    .where(
                        EpisodicMemoryRow.agent_id == uuid.UUID(agent_id),
                        EpisodicMemoryRow.summary.ilike(f"%{keyword}%"),
                    )
                    .order_by(desc(EpisodicMemoryRow.created_at))
                    .limit(limit)
                )
                result = await session.execute(stmt)
                rows = result.scalars().all()
                return [
                    {
                        "event_type": r.event_type,
                        "summary": r.summary,
                        "importance": r.importance,
                        "when": r.created_at.isoformat() if r.created_at else "",
                    }
                    for r in rows
                ]
        except Exception:
            logger.warning("Episodic keyword recall failed for %s", agent_id, exc_info=True)
            return []
