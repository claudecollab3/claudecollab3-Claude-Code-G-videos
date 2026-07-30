"""In-process pub/sub hub bridging the notification dispatcher to
connected WebSocket clients — the delivery mechanism behind the "desktop"
and "push" channels below, since actual OS-level desktop notifications and
mobile push (APNs/FCM) require a native app shell or registered device
tokens this project doesn't have. A browser dashboard renders these as
toasts and/or via the browser's own Notification API; see
`backend/app/api/v1/notifications.py` for the WebSocket endpoint.
"""

import asyncio

from notifications.events import NotificationMessage


class NotificationHub:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[NotificationMessage]] = set()

    def subscribe(self) -> "asyncio.Queue[NotificationMessage]":
        queue: asyncio.Queue[NotificationMessage] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: "asyncio.Queue[NotificationMessage]") -> None:
        self._subscribers.discard(queue)

    async def publish(self, message: NotificationMessage) -> None:
        for queue in list(self._subscribers):
            await queue.put(message)


_hub = NotificationHub()


def get_hub() -> NotificationHub:
    return _hub
