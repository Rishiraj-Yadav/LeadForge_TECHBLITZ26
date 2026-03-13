"""Base helpers for Beanie document models."""

from datetime import datetime, timezone
from pydantic import Field


class TimestampMixin:
    """Adds created_at / updated_at to any Beanie Document via mixin."""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
