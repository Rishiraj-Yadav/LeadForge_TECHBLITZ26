"""Rule-based lead scoring helpers."""


def classify_urgency(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ["today", "urgent", "asap", "immediately", "right now"]):
        return "high"
    if any(word in lowered for word in ["this week", "soon", "quick"]):
        return "medium"
    return "low"


def score_reasoning(score: float, legitimacy_score: float, urgency: str) -> str:
    if score >= 8:
        label = "High quality lead"
    elif score >= 5:
        label = "Moderate quality lead"
    else:
        label = "Low quality lead"
    return f"{label}; legitimacy={legitimacy_score:.1f}/10; urgency={urgency}."
