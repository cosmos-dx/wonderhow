from __future__ import annotations

import logging
from dataclasses import dataclass, field
from collections import Counter

from wonderhow.models.message import ChatMessage

logger = logging.getLogger(__name__)


@dataclass
class DebateRound:
    topic: str
    group_id: str
    round_number: int = 0
    max_rounds: int = 5
    agent_stances: dict[str, str] = field(default_factory=dict)
    arguments: list[ChatMessage] = field(default_factory=list)
    is_active: bool = True

    @property
    def is_complete(self) -> bool:
        return self.round_number >= self.max_rounds or not self.is_active

    def add_argument(self, message: ChatMessage, stance: str):
        self.arguments.append(message)
        self.agent_stances[message.agent_id] = stance

    def advance_round(self):
        self.round_number += 1
        if self.round_number >= self.max_rounds:
            self.is_active = False

    def tally_votes(self) -> dict[str, int]:
        return dict(Counter(self.agent_stances.values()))

    def consensus_reached(self) -> tuple[bool, str | None]:
        if not self.agent_stances:
            return False, None
        counts = self.tally_votes()
        total = len(self.agent_stances)
        for stance, count in counts.items():
            if count / total >= 0.7:
                return True, stance
        return False, None


class DebateManager:
    def __init__(self):
        self.active_debates: dict[str, DebateRound] = {}

    def start_debate(self, group_id: str, topic: str, max_rounds: int = 5) -> DebateRound:
        debate = DebateRound(topic=topic, group_id=group_id, max_rounds=max_rounds)
        self.active_debates[group_id] = debate
        logger.info("Debate started in group %s on topic: %s", group_id, topic)
        return debate

    def get_debate(self, group_id: str) -> DebateRound | None:
        return self.active_debates.get(group_id)

    def end_debate(self, group_id: str) -> DebateRound | None:
        debate = self.active_debates.pop(group_id, None)
        if debate:
            debate.is_active = False
            logger.info(
                "Debate ended in group %s. Votes: %s",
                group_id, debate.tally_votes(),
            )
        return debate

    def record_argument(self, group_id: str, message: ChatMessage, stance: str):
        debate = self.active_debates.get(group_id)
        if debate and debate.is_active:
            debate.add_argument(message, stance)
