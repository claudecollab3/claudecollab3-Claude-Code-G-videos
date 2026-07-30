from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEventResponse(BaseModel):
    external_id: str
    name: str
    currency: str
    impact: str
    event_time: datetime
    forecast: str | None
    previous: str | None
    actual: str | None


class NewsPolicyRequest(BaseModel):
    symbol: str = Field(max_length=32)


class NewsPolicyResponse(BaseModel):
    action: str
    reason: str
    upcoming_event: CalendarEventResponse | None
