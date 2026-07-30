"""Economic calendar integration: a pluggable provider interface plus a
generic HTTP-JSON client.

No specific calendar vendor is wired in — the spec doesn't name one, and
guessing a real provider's URL isn't something to fabricate. Configure
`ECONOMIC_CALENDAR_API_KEY` and `ECONOMIC_CALENDAR_BASE_URL` to point
`HttpCalendarProvider` at your provider's endpoint (adapt `_parse` if its
JSON shape differs from the one documented below). Until both are set,
`get_calendar_provider()` (see `ai/news/factory.py`) returns
`StaticCalendarProvider`, which yields an empty list rather than failing —
the rest of the pipeline degrades gracefully instead of crashing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from database.models.news_event import NewsImpact

# Re-exported for convenience so callers don't need to import from database.models directly.
__all__ = [
    "NewsImpact",
    "CalendarEvent",
    "EconomicCalendarProvider",
    "StaticCalendarProvider",
    "HttpCalendarProvider",
]


@dataclass
class CalendarEvent:
    external_id: str
    name: str
    currency: str
    impact: NewsImpact
    event_time: datetime
    forecast: str | None = None
    previous: str | None = None
    actual: str | None = None


class EconomicCalendarProvider(ABC):
    @abstractmethod
    async def upcoming_events(self, *, hours_ahead: int = 24) -> list[CalendarEvent]:
        raise NotImplementedError


class StaticCalendarProvider(EconomicCalendarProvider):
    """Returns a fixed, injected list — the default when no external
    provider is configured, and useful for tests."""

    def __init__(self, events: list[CalendarEvent] | None = None):
        self._events = events or []

    async def upcoming_events(self, *, hours_ahead: int = 24) -> list[CalendarEvent]:
        return list(self._events)


class HttpCalendarProvider(EconomicCalendarProvider):
    """Generic JSON HTTP client for an economic-calendar API. Expects an
    array of objects shaped like::

        {"id": str, "title": str, "country": str,
         "impact": "low"|"medium"|"high", "date": "<ISO-8601>",
         "forecast": str|null, "previous": str|null, "actual": str|null}

    Adapt `_parse` if your provider's schema differs.
    """

    def __init__(self, *, base_url: str, api_key: str, timeout: float = 10.0):
        self._base_url = base_url
        self._api_key = api_key
        self._timeout = timeout

    async def upcoming_events(self, *, hours_ahead: int = 24) -> list[CalendarEvent]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                self._base_url,
                params={"hours": hours_ahead},
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            return [self._parse(item) for item in response.json()]

    @staticmethod
    def _parse(item: dict[str, Any]) -> CalendarEvent:
        return CalendarEvent(
            external_id=str(item["id"]),
            name=item["title"],
            currency=item["country"],
            impact=NewsImpact(item["impact"]),
            event_time=datetime.fromisoformat(item["date"]),
            forecast=item.get("forecast"),
            previous=item.get("previous"),
            actual=item.get("actual"),
        )
