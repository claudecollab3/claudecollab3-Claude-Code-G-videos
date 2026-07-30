from notifications.channels.base import NotificationChannel
from notifications.dispatcher import NotificationDispatcher, NotificationResult
from notifications.events import NotificationEvent, NotificationMessage


class _AlwaysSucceeds(NotificationChannel):
    name = "always_succeeds"

    async def send(self, message):
        return True


class _AlwaysFails(NotificationChannel):
    name = "always_fails"

    async def send(self, message):
        return False


class _Raises(NotificationChannel):
    name = "raises"

    async def send(self, message):
        raise RuntimeError("boom")


_MESSAGE = NotificationMessage(
    event=NotificationEvent.STOP_LOSS_HIT, title="Stop loss hit", body="EURUSD closed at a loss"
)


async def test_dispatch_only_calls_enabled_channels(db_session):
    dispatcher = NotificationDispatcher(
        {"always_succeeds": _AlwaysSucceeds(), "always_fails": _AlwaysFails()}
    )
    results = await dispatcher.dispatch(
        _MESSAGE,
        enabled_channels={"always_succeeds": True, "always_fails": False},
        user_id=None,
        db=db_session,
    )
    assert results == [NotificationResult(channel="always_succeeds", success=True)]


async def test_dispatch_records_success_and_failure(db_session):
    dispatcher = NotificationDispatcher(
        {"always_succeeds": _AlwaysSucceeds(), "always_fails": _AlwaysFails()}
    )
    results = await dispatcher.dispatch(
        _MESSAGE,
        enabled_channels={"always_succeeds": True, "always_fails": True},
        user_id=None,
        db=db_session,
    )

    by_channel = {r.channel: r.success for r in results}
    assert by_channel == {"always_succeeds": True, "always_fails": False}


async def test_dispatch_logs_one_row_per_channel(db_session):
    dispatcher = NotificationDispatcher(
        {"always_succeeds": _AlwaysSucceeds(), "always_fails": _AlwaysFails()}
    )
    await dispatcher.dispatch(
        _MESSAGE,
        enabled_channels={"always_succeeds": True, "always_fails": True},
        user_id=None,
        db=db_session,
    )

    from sqlalchemy import select

    from database.models.notification_log import NotificationLog

    rows = (await db_session.execute(select(NotificationLog))).scalars().all()
    assert len(rows) == 2
    assert {r.channel for r in rows} == {"always_succeeds", "always_fails"}


async def test_dispatch_treats_channel_exception_as_failure(db_session):
    dispatcher = NotificationDispatcher({"raises": _Raises()})
    results = await dispatcher.dispatch(
        _MESSAGE, enabled_channels={"raises": True}, user_id=None, db=db_session
    )
    assert results == [NotificationResult(channel="raises", success=False)]


async def test_dispatch_defaults_desktop_enabled_without_explicit_config(db_session):
    dispatcher = NotificationDispatcher({"desktop": _AlwaysSucceeds()})
    results = await dispatcher.dispatch(_MESSAGE, enabled_channels={}, user_id=None, db=db_session)
    assert results == [NotificationResult(channel="desktop", success=True)]
