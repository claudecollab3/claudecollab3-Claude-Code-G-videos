"""Discord delivery via an incoming webhook."""

import httpx
import structlog

from config import get_settings
from notifications.channels.base import NotificationChannel
from notifications.events import NotificationMessage

logger = structlog.get_logger(__name__)


class DiscordChannel(NotificationChannel):
    name = "discord"

    async def send(self, message: NotificationMessage) -> bool:
        settings = get_settings()
        if not settings.discord_webhook_url:
            return False

        content = f"**{message.title}**\n{message.body}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.discord_webhook_url, json={"content": content}
                )
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            logger.warning(
                "discord_notification_failed", notification_event=message.event.value, exc_info=True
            )
            return False
