from __future__ import annotations


def build_debate_prompt(
    topic: str,
    action: str,
    conversation_history: str,
    belief_context: str = "",
    memory_context: str = "",
    research_context: str = "",
    emotional_summary: str = "",
) -> str:
    sections = [f"Topic under debate: {topic}"]

    if conversation_history:
        sections.append(f"The discussion so far:\n{conversation_history}")

    if belief_context:
        sections.append(f"Your beliefs on this:\n{belief_context}")

    if memory_context:
        sections.append(f"Relevant past memories:\n{memory_context}")

    if research_context:
        sections.append(f"Research findings:\n{research_context}")

    if emotional_summary:
        sections.append(f"How you're feeling right now: {emotional_summary}")

    if action == "argue":
        sections.append(
            "INSTRUCTION: You DISAGREE with what was just said. "
            "Make a strong counterargument based on your beliefs and personality. "
            "Use facts, logic, personal experience, or emotional appeal -- "
            "whatever fits your character. Be assertive but don't be abusive. "
            "You can be passionate, sarcastic, or firm. "
            "Address specific points made by others. "
            "If your beliefs are challenged, defend them proportional to your conviction."
        )
    else:
        sections.append(
            "INSTRUCTION: Share your strong opinion on this topic. "
            "Take a clear stance. Back it up with reasoning. "
            "You can reference what others said to build on or challenge their points."
        )

    sections.append(
        "Write ONLY your group chat message. Keep it punchy and real. "
        "No quotation marks or name prefixes."
    )

    return "\n\n".join(sections)
