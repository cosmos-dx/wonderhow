from __future__ import annotations

import re
import logging
from openai import AsyncOpenAI

from wonderhow.config import settings
from wonderhow.engine.agent_engine import AgentEngine
from wonderhow.models.message import ChatMessage

logger = logging.getLogger(__name__)

NOISE_PATTERNS = [
    r"^(hi+|hey+|hello+|yo+|sup|hii+|helo+|namaste|namaskar)[\s!.?]*$",
    r"^(ok+|okay+|k+|hmm+|hm+|ah+|oh+|lol+|haha+|hehe+|xd+|rofl)[\s!.?]*$",
    r"^(thanks|thankyou|thank you|thx|ty)[\s!.?]*$",
    r"^(bye+|goodbye|good night|gn|cya)[\s!.?]*$",
    r"^[.!?]+$",
    r"^[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\s]+$",
]

_compiled_noise = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


def parse_mentions(text: str) -> list[str]:
    """Extract @mentioned names from a message."""
    return [m.lower() for m in re.findall(r"@(\w+)", text)]


def is_noise(text: str) -> bool:
    """Check if a message is just noise/spam with no substance."""
    cleaned = text.strip()
    if len(cleaned) < 4:
        return True
    for pattern in _compiled_noise:
        if pattern.match(cleaned):
            return True
    return False


def find_mentioned_agents(
    mentions: list[str], agents: list[AgentEngine]
) -> list[AgentEngine]:
    """Match @mentions to actual agents (fuzzy name matching)."""
    matched = []
    for mention in mentions:
        mention_lower = mention.lower()
        for agent in agents:
            name_lower = agent.name.lower()
            first_name = name_lower.split()[0]
            if (
                mention_lower == name_lower
                or mention_lower == first_name
                or mention_lower in name_lower
                or name_lower.startswith(mention_lower)
            ):
                if agent not in matched:
                    matched.append(agent)
                break
    return matched


async def score_relevance(
    user_text: str, group_theme: str, current_topic: str, agents: list[AgentEngine]
) -> dict:
    """Use LLM to quickly assess how relevant a user message is to the group.

    Returns: {relevance: 0-1, topic_shift: str|None, provokes_agents: list[str]}
    """
    agent_descriptions = "\n".join(
        f"- {a.name}: {a.persona.profession}, interests={a.persona.interests[:3]}, "
        f"temperament={a.persona.temperament}"
        for a in agents
    )

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    try:
        resp = await client.chat.completions.create(
            model=settings.openai_model_fast,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You assess user messages in a group chat with AI agents. "
                        "Respond with JSON only.\n"
                        f"Group theme: {group_theme}\n"
                        f"Current topic: {current_topic}\n"
                        f"Agents in group:\n{agent_descriptions}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f'User message: "{user_text}"\n\n'
                        "Assess this message. Return JSON:\n"
                        "{\n"
                        '  "relevance": 0.0 to 1.0 (how relevant to this group\'s theme),\n'
                        '  "topic_shift": null or "new topic string" (if user is introducing a new discussion topic),\n'
                        '  "provoked_agents": ["name1"] (agents whose beliefs/interests are directly challenged or addressed),\n'
                        '  "is_question": true/false,\n'
                        '  "is_provocative": true/false (challenges someone\'s belief strongly)\n'
                        "}"
                    ),
                },
            ],
            max_tokens=200,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        import json
        return json.loads(resp.choices[0].message.content.strip())
    except Exception:
        logger.warning("Relevance scoring failed", exc_info=True)
        return {"relevance": 0.5, "topic_shift": None, "provoked_agents": [], "is_question": False, "is_provocative": False}
