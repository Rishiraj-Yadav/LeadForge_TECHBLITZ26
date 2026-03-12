"""Lightweight intent classification for conversations."""


def classify_intent(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["buy", "book", "ready", "go ahead", "proceed"]):
        return "ready_to_buy"
    if any(term in lowered for term in ["call me", "phone", "talk", "speak"]):
        return "needs_call"
    if any(term in lowered for term in ["but", "however", "expensive", "not sure", "problem"]):
        return "objection"
    if any(term in lowered for term in ["what", "how", "when", "can you", "do you"]):
        return "question"
    return "qualification"
