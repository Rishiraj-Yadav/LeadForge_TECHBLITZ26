"""Telegram message templates for notifications."""


def lead_notification_card(lead_data: dict) -> str:
    """Format a lead summary card for rep notification."""
    name = lead_data.get("customer_name", "Unknown")
    source = lead_data.get("source", "unknown")
    score = lead_data.get("score", 0)
    message = lead_data.get("message", "No message")
    reasoning = lead_data.get("score_reasoning", "")

    priority = "HIGH" if score >= 8 else "MEDIUM" if score >= 5 else "LOW"

    return (
        f"New Lead Alert\n\n"
        f"Name: {name}\n"
        f"Source: {source.title()}\n"
        f"Score: {score}/10 [{priority}]\n"
        f"Message: {message[:200]}\n"
        f"Analysis: {reasoning[:200]}\n\n"
        f"Lead ID: {lead_data.get('id', 'N/A')}"
    )


def pipeline_summary(leads: list[dict]) -> str:
    """Format a pipeline summary for the rep."""
    if not leads:
        return "Pipeline Summary\n\nNo active leads today."

    lines = ["Pipeline Summary\n"]
    for lead in leads:
        lines.append(
            f"- {lead.get('customer_name', 'Unknown')} | {lead.get('stage', 'new')} | Score: {lead.get('score', 0)}"
        )
    return "\n".join(lines)