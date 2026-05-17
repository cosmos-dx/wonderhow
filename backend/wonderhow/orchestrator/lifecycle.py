from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime

from wonderhow.config import settings
from wonderhow.engine.agent_engine import AgentEngine
from wonderhow.engine.debate_manager import DebateManager
from wonderhow.engine.emotional_state import natural_decay
from wonderhow.knowledge.web_search import WebSearcher
from wonderhow.knowledge.news_fetcher import NewsFetcher
from wonderhow.knowledge.fact_checker import FactChecker
from wonderhow.knowledge.topic_tracker import TopicTracker
from wonderhow.memory.short_term import ShortTermMemory
from wonderhow.memory.episodic import EpisodicMemory
from wonderhow.memory.semantic import SemanticMemory
from wonderhow.memory.social_graph import SocialGraph
from wonderhow.models.message import ChatMessage
from wonderhow.orchestrator.event_bus import EventBus
from wonderhow.orchestrator.group_manager import GroupManager
from wonderhow.orchestrator.scheduler import AgentScheduler

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main lifecycle loop that drives the entire simulation."""

    def __init__(self):
        self.group_manager = GroupManager()
        self.scheduler = AgentScheduler()
        self.debate_manager = DebateManager()
        self.event_bus = EventBus()

        self.short_term = ShortTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.social_graph = SocialGraph()

        self.web_searcher = WebSearcher()
        self.news_fetcher = NewsFetcher()
        self.fact_checker = FactChecker()
        self.topic_tracker: TopicTracker | None = None

        self._running = False
        self.tick_count = 0
        self.current_topics: dict[str, str] = {}
        self._ws_broadcast: list = []

    def register_ws_callback(self, callback):
        self._ws_broadcast.append(callback)

    def unregister_ws_callback(self, callback):
        self._ws_broadcast = [cb for cb in self._ws_broadcast if cb is not callback]

    async def _broadcast_message(self, message: ChatMessage):
        for callback in self._ws_broadcast:
            try:
                await callback(message)
            except Exception:
                logger.warning("WebSocket broadcast failed", exc_info=True)

    async def initialize(self):
        self.group_manager.load_groups_from_files()
        await self.short_term.connect()
        self.semantic.connect()
        self.topic_tracker = TopicTracker(self.news_fetcher, self.web_searcher)

        for agent in self.group_manager.get_all_agents():
            self.social_graph.add_agent(agent.id, agent.name)

        for group_id, agent_ids in self.group_manager.group_agents.items():
            for i, aid in enumerate(agent_ids):
                for j, other_id in enumerate(agent_ids):
                    if i != j:
                        self.social_graph.update_relationship(aid, other_id, trust_delta=0.1)

        logger.info(
            "Orchestrator initialized: %d groups, %d agents",
            len(self.group_manager.groups),
            len(self.group_manager.agents),
        )

    async def run(self):
        self._running = True
        await self.initialize()

        event_task = asyncio.create_task(self.event_bus.run())

        try:
            while self._running:
                await self._tick()
                await asyncio.sleep(settings.tick_interval_seconds)
        except asyncio.CancelledError:
            pass
        finally:
            self.event_bus.stop()
            event_task.cancel()
            await self.web_searcher.close()
            await self.news_fetcher.close()

    def stop(self):
        self._running = False

    async def _tick(self):
        self.tick_count += 1
        logger.debug("=== Tick %d ===", self.tick_count)

        for group in self.group_manager.get_all_groups():
            if not group.is_active:
                continue
            await self._process_group(group.id, group.theme)

        if self.tick_count % 10 == 0:
            for agent in self.group_manager.get_all_agents():
                agent.emotional_state = natural_decay(agent.emotional_state)

    async def _process_group(self, group_id: str, theme: str):
        agents = self.group_manager.get_group_agents(group_id)
        if not agents:
            return

        if group_id not in self.current_topics or self.tick_count % 20 == 0:
            topic = await self.topic_tracker.get_trending_topic(theme)
            if topic:
                self.current_topics[group_id] = topic
                logger.info("New topic for group %s: %s", group_id, topic)

                system_msg = ChatMessage(
                    group_id=group_id,
                    agent_id="system",
                    agent_name="System",
                    content=f"New discussion topic: {topic}",
                    message_type="system",
                )
                await self.short_term.add_message(group_id, system_msg)
                await self._broadcast_message(system_msg)

        topic = self.current_topics.get(group_id, "general discussion")
        recent = await self.short_term.get_recent(group_id, count=15)

        selected = self.scheduler.select_agents(agents, topic, max_active=2)

        for agent in selected:
            await self._agent_turn(agent, group_id, topic, recent, agents)
            await asyncio.sleep(1)

    async def _agent_turn(
        self,
        agent: AgentEngine,
        group_id: str,
        topic: str,
        recent_messages: list[ChatMessage],
        all_agents: list[AgentEngine],
    ):
        for msg in recent_messages[-5:]:
            if msg.agent_id != agent.id and msg.agent_id != "system":
                agent.process_incoming_message(msg, topic)

        action = agent.decide(recent_messages, topic)
        logger.debug("Agent %s decided: %s", agent.name, action)

        if action in ("idle", "ignore"):
            return

        memory_context = await self._get_memory_context(agent, topic)

        research_context = ""
        if action == "research":
            results = await self.web_searcher.search(f"{topic} India", max_results=3)
            if results:
                research_context = "\n".join(
                    f"- {r['title']}: {r['content'][:200]}" for r in results[:3]
                )
                self.semantic.store(
                    agent.id,
                    f"research_{uuid.uuid4().hex[:8]}",
                    research_context,
                    {"topic": topic, "type": "research"},
                )

        response_text = await agent.generate_response(
            recent_messages, topic, action,
            memory_context=memory_context,
            research_context=research_context,
        )

        if not response_text:
            return

        tone = self._classify_tone(action, agent.emotional_state.dominant_emotion)

        message = ChatMessage(
            group_id=group_id,
            agent_id=agent.id,
            agent_name=agent.name,
            content=response_text,
            message_type="debate" if action == "argue" else "chat",
            emotional_tone=tone,
        )

        await self.short_term.add_message(group_id, message)
        await self._broadcast_message(message)

        self.semantic.store(
            agent.id,
            f"msg_{message.id}",
            response_text,
            {"topic": topic, "action": action, "group_id": group_id},
        )

        await self.episodic.store(
            agent_id=agent.id,
            event_type=f"spoke_{action}",
            summary=f"Discussed '{topic}': {response_text[:100]}...",
            details={"topic": topic, "action": action, "group_id": group_id},
            importance=0.6 if action == "argue" else 0.4,
        )

        for other in all_agents:
            if other.id != agent.id:
                is_challenge = action == "argue"
                delta = -0.05 if is_challenge else 0.03
                self.social_graph.update_relationship(
                    other.id, agent.id,
                    trust_delta=delta,
                    interaction_type=action,
                )

    async def _get_memory_context(self, agent: AgentEngine, topic: str) -> str:
        parts = []

        episodic_memories = await self.episodic.recall_about(agent.id, topic, limit=3)
        if episodic_memories:
            parts.append("Past experiences:")
            for mem in episodic_memories:
                parts.append(f"  - {mem['summary']}")

        semantic_results = self.semantic.query(agent.id, topic, n_results=3)
        if semantic_results:
            parts.append("Related knowledge:")
            for r in semantic_results:
                parts.append(f"  - {r['text'][:150]}")

        relationships = self.social_graph.get_relationships(agent.id)
        if relationships:
            notable = [r for r in relationships if abs(r["trust"]) > 0.2]
            if notable:
                parts.append("Social context:")
                for r in notable[:3]:
                    sentiment = "trust" if r["trust"] > 0 else "distrust"
                    parts.append(f"  - You {sentiment} {r['agent_name']} ({r['trust']:.1f})")

        return "\n".join(parts) if parts else ""

    def _classify_tone(self, action: str, dominant_emotion: str) -> str:
        if action == "argue":
            return "confrontational"
        if action == "agree":
            return "supportive"
        if action == "joke":
            return "humorous"
        return dominant_emotion

    async def handle_user_message(self, group_slug: str, user_text: str, username: str = "User"):
        """Process a message from a real human user."""
        from wonderhow.engine.user_message_handler import (
            parse_mentions, is_noise, find_mentioned_agents, score_relevance,
        )

        group = self.group_manager.get_group_by_slug(group_slug)
        if not group:
            return

        user_msg = ChatMessage(
            group_id=group.id,
            agent_id="user",
            agent_name=username,
            content=user_text,
            message_type="user",
            emotional_tone="neutral",
        )
        await self.short_term.add_message(group.id, user_msg)
        await self._broadcast_message(user_msg)

        agents = self.group_manager.get_group_agents(group.id)
        if not agents:
            return

        mentions = parse_mentions(user_text)
        mentioned_agents = find_mentioned_agents(mentions, agents)

        if mentioned_agents:
            recent = await self.short_term.get_recent(group.id, count=15)
            topic = self.current_topics.get(group.id, "general discussion")
            for agent in mentioned_agents:
                await self._agent_reply_to_user(agent, group.id, topic, recent, agents, user_text)
                await asyncio.sleep(1.5)
            return

        if is_noise(user_text):
            import random
            if random.random() < 0.15:
                chosen = random.choice(agents)
                recent = await self.short_term.get_recent(group.id, count=15)
                topic = self.current_topics.get(group.id, "general discussion")
                await self._agent_reply_to_user(
                    chosen, group.id, topic, recent, agents, user_text, action="dismiss_noise"
                )
            return

        topic = self.current_topics.get(group.id, "general discussion")
        assessment = await score_relevance(user_text, group.theme, topic, agents)
        relevance = assessment.get("relevance", 0.5)

        new_topic = assessment.get("topic_shift")
        if new_topic and relevance > 0.5:
            self.current_topics[group.id] = new_topic
            system_msg = ChatMessage(
                group_id=group.id,
                agent_id="system",
                agent_name="System",
                content=f"Topic shifted to: {new_topic}",
                message_type="system",
            )
            await self.short_term.add_message(group.id, system_msg)
            await self._broadcast_message(system_msg)
            topic = new_topic

        if relevance < 0.25:
            return

        recent = await self.short_term.get_recent(group.id, count=15)

        provoked_names = [n.lower() for n in assessment.get("provoked_agents", [])]
        responders = []
        for agent in agents:
            if agent.name.lower() in provoked_names or agent.name.split()[0].lower() in provoked_names:
                responders.append(agent)

        if not responders:
            import random
            if assessment.get("is_question"):
                best = max(agents, key=lambda a: a.emotional_state.engagement)
                responders = [best]
            elif relevance > 0.6:
                count = min(2, len(agents))
                scored = sorted(agents, key=lambda a: a.emotional_state.willingness_to_speak, reverse=True)
                responders = scored[:count]
            elif relevance > 0.4:
                scored = sorted(agents, key=lambda a: a.emotional_state.willingness_to_speak, reverse=True)
                responders = [scored[0]] if scored else []

        for agent in responders:
            await asyncio.sleep(2)
            await self._agent_reply_to_user(agent, group.id, topic, recent, agents, user_text)

    async def _agent_reply_to_user(
        self,
        agent: AgentEngine,
        group_id: str,
        topic: str,
        recent_messages: list[ChatMessage],
        all_agents: list[AgentEngine],
        user_text: str,
        action: str = "reply_to_user",
    ):
        """Have a specific agent reply to the user's message."""
        memory_context = await self._get_memory_context(agent, topic)

        response_text = await agent.generate_response(
            recent_messages, topic, action,
            memory_context=memory_context,
        )

        if not response_text:
            return

        tone = self._classify_tone("speak", agent.emotional_state.dominant_emotion)

        message = ChatMessage(
            group_id=group_id,
            agent_id=agent.id,
            agent_name=agent.name,
            content=response_text,
            message_type="chat",
            emotional_tone=tone,
        )

        await self.short_term.add_message(group_id, message)
        await self._broadcast_message(message)

        agent.absorb_information(topic, user_text[:100], 0.4, "user")

    def get_status(self) -> dict:
        return {
            "running": self._running,
            "tick_count": self.tick_count,
            "active_groups": len(self.group_manager.groups),
            "active_agents": len(self.group_manager.agents),
            "current_topics": self.current_topics,
        }
