"""Placeholder FAQ / product lookup.

Replace this with a proper per-business knowledge base.
"""


def answer_common_question(question: str) -> str | None:
    lowered = question.lower()
    if "price" in lowered or "cost" in lowered:
        return "Pricing depends on the exact requirements. I can help narrow that down with a few details."
    if "availability" in lowered:
        return "Availability depends on date and capacity. Share your preferred date and I will check the next best option."
    return None
