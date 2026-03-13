"""Phone number utilities using the phonenumbers library."""

import phonenumbers


def normalize_phone(raw: str, default_region: str = "IN") -> str | None:
    """Return E.164 formatted phone number or None if invalid."""
    try:
        parsed = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None


def phone_to_channel_id(phone_e164: str) -> str:
    """Normalize a phone-based identifier for downstream channel usage."""
    return phone_e164.lstrip("+")
