"""Telegram delivery via the Bot API's sendMessage endpoint."""

import httpx
import structlog

from config import get_settings
from notifications.channels.base import NotificationChannel
from notifications.events import NotificationMessage

logger = structlog.get_logger(__name__)


class TelegramChannel(NotificationChannel):
    name = "telegram"

    async def send(self, message: NotificationMessage) -> bool:
        settings = get_settings()
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            return False

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        text = f"*{message.title}*\n{message.body}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={
                        "chat_id": settings.telegram_chat_id,
                        "text": text,
                        "parse_mode": "Markdown",
                    },
                )
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            logger.warning(
                "telegram_notification_failed",
                notification_event=message.event.value,
                exc_info=True,
            )
            return False
