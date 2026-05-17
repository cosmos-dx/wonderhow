from __future__ import annotations


def build_opinion_prompt(
    topic: str,
    action: str,
    conversation_history: str,
    belief_context: str = "",
    memory_context: str = "",
    research_context: str = "",
) -> str:
    sections = [f"Current topic being discussed: {topic}"]

    if conversation_history:
        sections.append(f"Recent conversation:\n{conversation_history}")

    if belief_context:
        sections.append(f"Your existing beliefs on related topics:\n{belief_context}")

    if memory_context:
        sections.append(f"Relevant memories from past discussions:\n{memory_context}")

    if research_context:
        sections.append(
            f"Information you just found from research:\n{research_context}"
        )

    action_instructions = {
        "agree": (
            "You find yourself agreeing with the recent messages. "
            "Express your agreement naturally, and add your own perspective or supporting point. "
            "Don't just say 'I agree' -- add value."
        ),
        "research": (
            "You've done some research on this topic and want to share what you found. "
            "Present the information naturally, citing where you learned it. "
            "Give your opinion on the findings."
        ),
        "joke": (
            "The conversation reminds you of something funny or ironic. "
            "Make a witty comment, joke, or observation that's relevant to the discussion. "
            "Keep it natural to your character."
        ),
        "speak": (
            "Share your thoughts on this topic. "
            "Draw from your personality, experiences, and beliefs. "
            "Be genuine and specific."
        ),
        "reply_to_user": (
            "A real human user just sent a message in the group chat. "
            "They tagged you specifically or said something that you feel compelled to respond to. "
            "Reply to them directly and naturally, as you would in a real group chat. "
            "Be conversational. You can address them as 'you' or 'bro'/'yaar' etc based on your style. "
            "If they asked a question, answer it from your perspective. "
            "If they made a point, react to it genuinely."
        ),
        "dismiss_noise": (
            "Someone sent a low-effort or irrelevant message in the group. "
            "You can either ignore it completely (preferred) or give a very brief dismissive reply "
            "if it's disrupting an ongoing discussion. Keep it to one short sentence max."
        ),
    }

    instruction = action_instructions.get(
        action,
        "Respond naturally to the conversation based on your character.",
    )

    sections.append(f"What to do: {instruction}")
    sections.append(
        "Write ONLY your message as it would appear in the group chat. "
        "No quotation marks, no prefixes like your name. Just the message text."
    )

    return "\n\n".join(sections)
