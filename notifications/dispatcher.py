"""Fan-out dispatcher: sends a NotificationMessage to every channel a user
has enabled, logging each attempt to the database for audit."""

import uuid
from dataclasses import dataclass

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.notification_log_repository import NotificationLogRepository
from notifications.channels.base import NotificationChannel
from notifications.channels.desktop import DesktopChannel
from notifications.channels.discord import DiscordChannel
from notifications.channels.email import EmailChannel
from notifications.channels.push import PushChannel
from notifications.channels.telegram import TelegramChannel
from notifications.events import NotificationMessage

logger = structlog.get_logger(__name__)

# "desktop" defaults on (no external config needed, delivered in-app over
# the WebSocket); everything else is opt-in since it requires configuring
# real external credentials (bot token, webhook, SMTP).
DEFAULT_ENABLED_CHANNELS: dict[str, bool] = {
    "desktop": True,
    "push": False,
    "telegram": False,
    "discord": False,
    "email": False,
}


@dataclass
class NotificationResult:
    channel: str
    success: bool


def build_default_channels() -> dict[str, NotificationChannel]:
    return {
        "desktop": DesktopChannel(),
        "push": PushChannel(),
        "telegram": TelegramChannel(),
        "discord": DiscordChannel(),
        "email": EmailChannel(),
    }


class NotificationDispatcher:
    def __init__(self, channels: dict[str, NotificationChannel] | None = None):
        self._channels = channels or build_default_channels()

    async def dispatch(
        self,
        message: NotificationMessage,
        *,
        enabled_channels: dict[str, bool],
        user_id: uuid.UUID | None,
        db: AsyncSession,
    ) -> list[NotificationResult]:
        merged_enabled = {**DEFAULT_ENABLED_CHANNELS, **enabled_channels}
        log_repository = NotificationLogRepository(db)
        results: list[NotificationResult] = []

        for name, channel in self._channels.items():
            if not merged_enabled.get(name, False):
                continue

            try:
                success = await channel.send(message)
            except Exception:
                logger.warning(
                    "notification_channel_failed",
                    channel=name,
                    notification_event=message.event.value,
                    exc_info=True,
                )
                success = False

            results.append(NotificationResult(channel=name, success=success))
            await log_repository.create(
                user_id=user_id,
                event=message.event.value,
                channel=name,
                success=success,
                title=message.title,
                body=message.body,
            )

        return results
