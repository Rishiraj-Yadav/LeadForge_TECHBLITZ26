"""Simple personalization helpers."""


def generate_personalized_opening(lead: dict) -> str:
    name = lead.get("customer_name") or "there"
    details = lead.get("details", {})
    detail_bits = []
    for key in ["event_type", "guest_count", "date", "location", "budget"]:
        if key in details and details[key]:
            detail_bits.append(f"{key.replace('_', ' ')}: {details[key]}")
    context = f" I noted {', '.join(detail_bits)}." if detail_bits else ""
    return f"Hi {name}, thanks for reaching out.{context}"
