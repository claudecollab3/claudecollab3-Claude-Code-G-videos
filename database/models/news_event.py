"""Persisted economic calendar events, fetched from a configured
EconomicCalendarProvider (see `ai/news/calendar.py`) and kept for
history/audit and the pre-trade news policy check."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDPKMixin


class NewsImpact(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NewsEvent(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "news_events"

    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    impact: Mapped[NewsImpact] = mapped_column(Enum(NewsImpact, name="news_impact"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    forecast: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actual: Mapped[str | None] = mapped_column(String(64), nullable=True)
