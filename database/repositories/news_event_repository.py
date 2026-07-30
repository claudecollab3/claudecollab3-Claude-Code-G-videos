"""Query layer for persisted economic calendar events."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.news_event import NewsEvent

if TYPE_CHECKING:
    from ai.news.calendar import CalendarEvent


class NewsEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert(self, event: "CalendarEvent") -> NewsEvent:
        result = await self.db.execute(
            select(NewsEvent).where(NewsEvent.external_id == event.external_id)
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            existing = NewsEvent(external_id=event.external_id)
            self.db.add(existing)

        existing.name = event.name
        existing.currency = event.currency
        existing.impact = event.impact
        existing.event_time = event.event_time
        existing.forecast = event.forecast
        existing.previous = event.previous
        existing.actual = event.actual
        await self.db.flush()
        return existing

    async def upcoming(self, *, now: datetime, hours_ahead: int = 24) -> list[NewsEvent]:
        result = await self.db.execute(
            select(NewsEvent)
            .where(
                NewsEvent.event_time >= now,
                NewsEvent.event_time <= now + timedelta(hours=hours_ahead),
            )
            .order_by(NewsEvent.event_time)
        )
        return list(result.scalars().all())
