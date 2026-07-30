"""Desktop notification channel: publishes to the in-process hub, which the
dashboard's WebSocket connection consumes and renders via the browser's
Notification API. See `notifications/hub.py` for why this isn't a native
OS-level hook."""

from notifications.channels.base import NotificationChannel
from notifications.events import NotificationMessage
from notifications.hub import get_hub


class DesktopChannel(NotificationChannel):
    name = "desktop"

    async def send(self, message: NotificationMessage) -> bool:
        await get_hub().publish(message)
        return True
