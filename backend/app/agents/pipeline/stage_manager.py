"""Pipeline stage classification helpers."""


def determine_stage(intent: str, rep_decision: str = "approved") -> str:
    if rep_decision == "rejected":
        return "lost"
    if intent == "ready_to_buy":
        return "proposal"
    if intent in {"question", "qualification"}:
        return "qualified"
    if intent == "needs_call":
        return "contacted"
    return "contacted"
