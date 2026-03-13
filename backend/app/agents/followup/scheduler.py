"""Follow-up timing logic."""

from datetime import datetime, timedelta, timezone


FOLLOW_UP_SEQUENCE_DAYS = [1, 2, 4, 7]


def next_followup_time(last_activity: datetime | None, attempt: int = 0) -> datetime:
    base = last_activity or datetime.now(timezone.utc)
    delay_days = FOLLOW_UP_SEQUENCE_DAYS[min(attempt, len(FOLLOW_UP_SEQUENCE_DAYS) - 1)]
    return base + timedelta(days=delay_days)
