"""Push notification channel: publishes to the in-process hub, same
delivery path as `desktop.py`. Real mobile push (APNs/FCM) needs a native
app registering device tokens, which is out of scope for this web backend;
kept as a distinct, independently toggleable channel from "desktop" per the
spec, even though both resolve to the same in-app delivery mechanism today.
"""

from notifications.channels.base import NotificationChannel
from notifications.events import NotificationMessage
from notifications.hub import get_hub


class PushChannel(NotificationChannel):
    name = "push"

    async def send(self, message: NotificationMessage) -> bool:
        await get_hub().publish(message)
        return True
