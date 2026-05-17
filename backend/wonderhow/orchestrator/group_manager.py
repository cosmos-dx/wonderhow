from __future__ import annotations

import json
import logging
from pathlib import Path

from wonderhow.models.agent import AgentProfile, PersonaConfig, EmotionalState
from wonderhow.models.belief import BeliefSystem
from wonderhow.models.group import GroupInfo, GroupConfig
from wonderhow.engine.agent_engine import AgentEngine

logger = logging.getLogger(__name__)

PERSONAS_DIR = Path(__file__).parent.parent / "personas"


class GroupManager:
    """Manages groups and their agent populations."""

    def __init__(self):
        self.groups: dict[str, GroupInfo] = {}
        self.agents: dict[str, AgentEngine] = {}
        self.group_agents: dict[str, list[str]] = {}

    def load_groups_from_files(self):
        if not PERSONAS_DIR.exists():
            logger.warning("Personas directory not found: %s", PERSONAS_DIR)
            return

        for filepath in PERSONAS_DIR.glob("*.json"):
            try:
                data = json.loads(filepath.read_text())
                group_data = data["group"]
                group = GroupInfo(
                    name=group_data["name"],
                    slug=group_data["slug"],
                    description=group_data.get("description", ""),
                    theme=group_data["theme"],
                    config=GroupConfig(**group_data.get("config", {})),
                )
                self.groups[group.id] = group
                self.group_agents[group.id] = []

                for agent_data in data.get("agents", []):
                    persona = PersonaConfig(**agent_data["persona"])
                    beliefs = BeliefSystem()
                    for topic, stance in agent_data.get("initial_beliefs", {}).items():
                        beliefs.set_belief(topic, stance, confidence=0.6)

                    profile = AgentProfile(persona=persona)
                    engine = AgentEngine(profile, beliefs)
                    self.agents[engine.id] = engine
                    self.group_agents[group.id].append(engine.id)
                    group.agent_ids.append(engine.id)

                logger.info(
                    "Loaded group '%s' with %d agents",
                    group.name, len(self.group_agents[group.id]),
                )
            except Exception:
                logger.exception("Failed to load group from %s", filepath)

    def get_group_agents(self, group_id: str) -> list[AgentEngine]:
        agent_ids = self.group_agents.get(group_id, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]

    def get_all_groups(self) -> list[GroupInfo]:
        return list(self.groups.values())

    def get_group_by_slug(self, slug: str) -> GroupInfo | None:
        for group in self.groups.values():
            if group.slug == slug:
                return group
        return None

    def get_agent(self, agent_id: str) -> AgentEngine | None:
        return self.agents.get(agent_id)

    def get_all_agents(self) -> list[AgentEngine]:
        return list(self.agents.values())

    def add_agent_to_group(self, group_id: str, engine: AgentEngine):
        self.agents[engine.id] = engine
        if group_id not in self.group_agents:
            self.group_agents[group_id] = []
        self.group_agents[group_id].append(engine.id)
        group = self.groups.get(group_id)
        if group:
            group.agent_ids.append(engine.id)
