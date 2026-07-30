import pytest

from notifications.channels.desktop import DesktopChannel
from notifications.channels.discord import DiscordChannel
from notifications.channels.email import EmailChannel
from notifications.channels.push import PushChannel
from notifications.channels.telegram import TelegramChannel
from notifications.events import NotificationEvent, NotificationMessage
from notifications.hub import get_hub

_MESSAGE = NotificationMessage(
    event=NotificationEvent.TRADE_OPENED, title="Trade opened", body="EURUSD long 0.1 lots"
)


@pytest.mark.parametrize("channel_cls", [TelegramChannel, DiscordChannel, EmailChannel])
async def test_external_channels_are_no_ops_when_unconfigured(channel_cls):
    channel = channel_cls()
    result = await channel.send(_MESSAGE)
    assert result is False


async def test_desktop_channel_publishes_to_hub():
    hub = get_hub()
    queue = hub.subscribe()
    try:
        result = await DesktopChannel().send(_MESSAGE)
        assert result is True
        received = await queue.get()
        assert received is _MESSAGE
    finally:
        hub.unsubscribe(queue)


async def test_push_channel_publishes_to_hub():
    hub = get_hub()
    queue = hub.subscribe()
    try:
        result = await PushChannel().send(_MESSAGE)
        assert result is True
        received = await queue.get()
        assert received is _MESSAGE
    finally:
        hub.unsubscribe(queue)
