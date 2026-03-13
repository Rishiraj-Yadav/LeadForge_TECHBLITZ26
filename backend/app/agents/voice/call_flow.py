"""Voice conversation flow helpers."""


def should_transfer_to_human(transcript: str) -> bool:
    lowered = transcript.lower()
    return any(term in lowered for term in ["human", "agent", "manager", "complaint", "refund"])
