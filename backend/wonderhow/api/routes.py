from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from wonderhow.api.schemas import GroupResponse, AgentResponse, MessageResponse, SystemStatus

router = APIRouter()


class CreateAgentRequest(BaseModel):
    name: str
    age: int = 25
    profession: str = ""
    background: str = ""
    political_bias: str = "centrist"
    temperament: str = "balanced"
    interests: list[str] = Field(default_factory=list)
    writing_style: str = "conversational"
    stubbornness: float = 0.5
    curiosity: float = 0.5
    aggressiveness: float = 0.3
    humor: float = 0.3
    core_beliefs: dict[str, str] = Field(default_factory=dict)
    group_slug: str


def _get_orchestrator():
    from wonderhow.main import orchestrator
    return orchestrator


@router.get("/status", response_model=SystemStatus)
async def get_status():
    orch = _get_orchestrator()
    status = orch.get_status()
    total_msgs = 0
    for group_id in orch.group_manager.groups:
        msgs = await orch.short_term.get_recent(group_id, count=1000)
        total_msgs += len(msgs)
    return SystemStatus(
        running=status["running"],
        tick_count=status["tick_count"],
        active_groups=status["active_groups"],
        active_agents=status["active_agents"],
        total_messages=total_msgs,
    )


@router.get("/groups", response_model=list[GroupResponse])
async def list_groups():
    orch = _get_orchestrator()
    groups = orch.group_manager.get_all_groups()
    result = []
    for g in groups:
        agents = orch.group_manager.get_group_agents(g.id)
        recent = await orch.short_term.get_recent(g.id, count=1)
        latest_msg = recent[0].content if recent else None
        latest_at = recent[0].created_at if recent else None
        result.append(GroupResponse(
            id=g.id,
            name=g.name,
            slug=g.slug,
            description=g.description,
            theme=g.theme,
            agent_count=len(agents),
            latest_message=latest_msg,
            latest_message_at=latest_at,
            is_active=g.is_active,
        ))
    return result


@router.get("/groups/{slug}")
async def get_group(slug: str):
    orch = _get_orchestrator()
    group = orch.group_manager.get_group_by_slug(slug)
    if not group:
        raise HTTPException(404, "Group not found")
    agents = orch.group_manager.get_group_agents(group.id)
    return {
        "id": group.id,
        "name": group.name,
        "slug": group.slug,
        "description": group.description,
        "theme": group.theme,
        "config": group.config.model_dump(),
        "current_topic": orch.current_topics.get(group.id, ""),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "persona": a.persona.model_dump(),
                "emotional_state": a.emotional_state.model_dump(),
            }
            for a in agents
        ],
    }


@router.get("/groups/{slug}/messages", response_model=list[MessageResponse])
async def get_group_messages(slug: str, limit: int = 50):
    orch = _get_orchestrator()
    group = orch.group_manager.get_group_by_slug(slug)
    if not group:
        raise HTTPException(404, "Group not found")
    messages = await orch.short_term.get_recent(group.id, count=limit)
    return [
        MessageResponse(
            id=m.id,
            group_id=m.group_id,
            agent_id=m.agent_id,
            agent_name=m.agent_name,
            content=m.content,
            message_type=m.message_type,
            emotional_tone=m.emotional_tone,
            sources=m.sources,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents():
    orch = _get_orchestrator()
    agents = orch.group_manager.get_all_agents()
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            persona=a.persona.model_dump(),
            emotional_state=a.emotional_state.model_dump(),
            beliefs={k: v.model_dump() for k, v in a.beliefs.beliefs.items()},
            social_graph={
                "relationships": orch.social_graph.get_relationships(a.id),
                "allies": orch.social_graph.get_allies(a.id),
                "rivals": orch.social_graph.get_rivals(a.id),
            },
            is_active=a.profile.is_active,
        )
        for a in agents
    ]


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    orch = _get_orchestrator()
    agent = orch.group_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    memories = await orch.episodic.recall(agent_id, limit=10)
    return {
        "id": agent.id,
        "name": agent.name,
        "persona": agent.persona.model_dump(),
        "emotional_state": agent.emotional_state.model_dump(),
        "beliefs": {k: v.model_dump() for k, v in agent.beliefs.beliefs.items()},
        "social_graph": {
            "relationships": orch.social_graph.get_relationships(agent.id),
            "allies": orch.social_graph.get_allies(agent.id),
            "rivals": orch.social_graph.get_rivals(agent.id),
        },
        "recent_memories": memories,
    }


@router.get("/social-graph")
async def get_social_graph():
    orch = _get_orchestrator()
    return orch.social_graph.get_visualization_data()


@router.post("/agents")
async def create_agent(req: CreateAgentRequest):
    from wonderhow.models.agent import AgentProfile, PersonaConfig
    from wonderhow.models.belief import BeliefSystem
    from wonderhow.engine.agent_engine import AgentEngine

    orch = _get_orchestrator()
    group = orch.group_manager.get_group_by_slug(req.group_slug)
    if not group:
        raise HTTPException(404, "Group not found")

    persona = PersonaConfig(
        name=req.name,
        age=req.age,
        profession=req.profession,
        background=req.background,
        political_bias=req.political_bias,
        temperament=req.temperament,
        interests=req.interests,
        writing_style=req.writing_style,
        stubbornness=req.stubbornness,
        curiosity=req.curiosity,
        aggressiveness=req.aggressiveness,
        humor=req.humor,
        core_beliefs=req.core_beliefs,
    )
    beliefs = BeliefSystem()
    for topic, stance in req.core_beliefs.items():
        beliefs.set_belief(topic, stance, confidence=0.7)

    profile = AgentProfile(persona=persona)
    engine = AgentEngine(profile, beliefs)

    orch.group_manager.add_agent_to_group(group.id, engine)
    orch.social_graph.add_agent(engine.id, engine.name)

    existing_agents = orch.group_manager.get_group_agents(group.id)
    for other in existing_agents:
        if other.id != engine.id:
            orch.social_graph.update_relationship(engine.id, other.id, trust_delta=0.05)

    return {
        "id": engine.id,
        "name": engine.name,
        "group_id": group.id,
        "group_slug": group.slug,
    }
