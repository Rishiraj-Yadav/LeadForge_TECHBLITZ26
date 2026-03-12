"""Outreach message templates."""


def initial_message(opening: str, original_message: str) -> str:
    return (
        f"{opening} Based on your message, I can help with this. "
        f"Could you share a bit more about what you need so I can suggest the best next step?\n\n"
        f"Your inquiry: \"{original_message[:180]}\""
    )
