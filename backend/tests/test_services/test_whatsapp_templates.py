from app.services.whatsapp.templates import lead_notification_card


def test_lead_notification_card_contains_name():
    text = lead_notification_card({"customer_name": "Asha", "source": "whatsapp", "score": 8})
    assert "Asha" in text
