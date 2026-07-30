from datetime import datetime

from pydantic import BaseModel, Field

from notifications.events import NotificationEvent


class TestNotificationRequest(BaseModel):
    event: NotificationEvent = NotificationEvent.TRADE_OPENED
    title: str = Field(default="Test notification", max_length=256)
    body: str = Field(default="This is a test notification.", max_length=1024)


class NotificationResultResponse(BaseModel):
    channel: str
    success: bool


class NotificationPreferencesResponse(BaseModel):
    channels: dict[str, bool]


class UpdateNotificationPreferenceRequest(BaseModel):
    channel: str = Field(max_length=32)
    enabled: bool


class NotificationLogResponse(BaseModel):
    event: str
    channel: str
    success: bool
    title: str
    body: str
    created_at: datetime
