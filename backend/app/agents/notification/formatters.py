"""Notification formatters for WhatsApp and Telegram."""


def format_rep_summary(lead: dict, research: dict, scoring: dict) -> str:
    return (
        f"New lead: {lead.get('customer_name') or lead.get('customer_phone') or 'Unknown'}\n"
        f"Source: {lead.get('source')}\n"
        f"Score: {scoring.get('score', 0)}/10\n"
        f"Reason: {scoring.get('reasoning', 'N/A')}\n"
        f"Research: {research.get('summary', 'N/A')}\n"
        f"Message: {lead.get('message', '')[:240]}"
    )
