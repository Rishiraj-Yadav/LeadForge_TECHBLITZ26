"""Date / time parsing helpers."""

from datetime import datetime, date
from dateutil import parser as dateutil_parser


def parse_date(text: str) -> date | None:
    try:
        return dateutil_parser.parse(text, fuzzy=True).date()
    except (ValueError, OverflowError):
        return None


def parse_datetime(text: str) -> datetime | None:
    try:
        return dateutil_parser.parse(text, fuzzy=True)
    except (ValueError, OverflowError):
        return None
