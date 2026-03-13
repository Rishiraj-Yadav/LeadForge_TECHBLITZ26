"""Notification formatters for Telegram-based rep alerts."""


def _safe(text: str) -> str:
    """Strip characters that break Telegram Markdown parsing."""
    for ch in ("_", "*", "[", "]", "`", "~"):
        text = text.replace(ch, "")
    return text


def format_rep_summary(lead: dict, research: dict, scoring: dict) -> str:
    name = _safe(str(lead.get("customer_name") or lead.get("customer_phone") or "Unknown"))
    source = _safe(str(lead.get("source", "")))
    reason = _safe(str(scoring.get("reasoning", "N/A")))
    message = _safe(str(lead.get("message", ""))[:240])
    score = scoring.get("score", 0)
    details = lead.get("details", {})

    # Build captured info section
    captured_lines = []
    field_labels = {
        "guest_count": "Guests",
        "date": "Date",
        "time": "Time",
        "event_type": "Event",
        "check_in": "Check-in",
        "check_out": "Check-out",
        "room_type": "Room",
        "budget": "Budget",
        "location": "Location",
        "property_type": "Property",
    }
    for key, label in field_labels.items():
        if key in details and details[key]:
            captured_lines.append(f"  {label}: {_safe(str(details[key]))}")

    # Include custom question answers (q1, q2, q3, q4, q5)
    for key in sorted(details.keys()):
        if key.startswith("q") and key[1:].isdigit() and details[key]:
            captured_lines.append(f"  Q{key[1:]}: {_safe(str(details[key]))}")

    captured_section = "\n".join(captured_lines) if captured_lines else "No details captured yet"
    priority = "HIGH" if score >= 8 else "MEDIUM" if score >= 5 else "LOW"
    score_bar = "🟢" * int(score) + "⚪" * (10 - int(score))

    return (
        f"{'🔴' if priority == 'HIGH' else '🟡' if priority == 'MEDIUM' else '⚪'} New Lead Alert [{priority}]\n\n"
        f"Name: {name}\n"
        f"Source: {source}\n"
        f"Score: {score}/10 {score_bar}\n\n"
        f"Captured Info:\n{captured_section}\n\n"
        f"Analysis: {reason}\n\n"
        f"Message: {message}\n\n"
        f"Lead ID: {lead.get('id', 'N/A')}"
    )

