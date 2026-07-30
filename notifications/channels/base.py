"""Common interface every notification channel implements."""

from abc import ABC, abstractmethod

from notifications.events import NotificationMessage


class NotificationChannel(ABC):
    name: str = "base"

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """Returns True if delivery was attempted and succeeded, False if
        the channel isn't configured or delivery failed. Never raises for
        an unconfigured channel -- that's a no-op, not an error."""
        raise NotImplementedError
