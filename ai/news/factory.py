"""Builds the configured EconomicCalendarProvider from settings."""

from ai.news.calendar import EconomicCalendarProvider, HttpCalendarProvider, StaticCalendarProvider
from config import get_settings


def get_calendar_provider() -> EconomicCalendarProvider:
    settings = get_settings()
    if settings.economic_calendar_api_key and settings.economic_calendar_base_url:
        return HttpCalendarProvider(
            base_url=settings.economic_calendar_base_url, api_key=settings.economic_calendar_api_key
        )
    return StaticCalendarProvider()
