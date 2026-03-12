"""Follow-up message sequences."""

FOLLOW_UP_MESSAGES = [
    "Just checking in in case this is still a priority for you.",
    "Following up with you. If timing is the issue, I can adjust options around your schedule.",
    "Wanted to circle back. If you still need help, I can make the next step simple.",
    "Final follow-up from my side. Reply anytime if you want to continue.",
]


def get_followup_message(attempt: int) -> str:
    return FOLLOW_UP_MESSAGES[min(attempt, len(FOLLOW_UP_MESSAGES) - 1)]
