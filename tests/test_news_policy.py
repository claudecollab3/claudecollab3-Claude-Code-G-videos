from datetime import UTC, datetime, timedelta

from ai.news.calendar import CalendarEvent, NewsImpact
from ai.news.policy import NewsAction, NewsPolicy

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _event(
    minutes_from_now: float, *, impact: NewsImpact = NewsImpact.HIGH, currency: str = "USD"
) -> CalendarEvent:
    return CalendarEvent(
        external_id="evt-1",
        name="Non-Farm Payrolls",
        currency=currency,
        impact=impact,
        event_time=NOW + timedelta(minutes=minutes_from_now),
    )


def test_trade_when_no_events():
    result = NewsPolicy().evaluate(
        events=[], now=NOW, news_trading_enabled=False, blackout_minutes=30
    )
    assert result.action == NewsAction.TRADE


def test_trade_when_only_low_impact_events():
    result = NewsPolicy().evaluate(
        events=[_event(10, impact=NewsImpact.LOW)],
        now=NOW,
        news_trading_enabled=False,
        blackout_minutes=30,
    )
    assert result.action == NewsAction.TRADE


def test_close_existing_when_high_impact_event_imminent():
    result = NewsPolicy().evaluate(
        events=[_event(5)], now=NOW, news_trading_enabled=False, blackout_minutes=30
    )
    assert result.action == NewsAction.CLOSE_EXISTING


def test_reduce_risk_within_blackout_but_not_imminent():
    result = NewsPolicy().evaluate(
        events=[_event(20)], now=NOW, news_trading_enabled=False, blackout_minutes=30
    )
    assert result.action == NewsAction.REDUCE_RISK


def test_wait_shortly_after_event_release():
    result = NewsPolicy().evaluate(
        events=[_event(-10)], now=NOW, news_trading_enabled=False, blackout_minutes=30
    )
    assert result.action == NewsAction.WAIT


def test_trade_once_outside_blackout_window_entirely():
    result = NewsPolicy().evaluate(
        events=[_event(120)], now=NOW, news_trading_enabled=False, blackout_minutes=30
    )
    assert result.action == NewsAction.TRADE


def test_news_trading_enabled_bypasses_blackout():
    result = NewsPolicy().evaluate(
        events=[_event(5)], now=NOW, news_trading_enabled=True, blackout_minutes=30
    )
    assert result.action == NewsAction.TRADE


def test_currency_filter_ignores_irrelevant_events():
    result = NewsPolicy().evaluate(
        events=[_event(5, currency="JPY")],
        now=NOW,
        news_trading_enabled=False,
        blackout_minutes=30,
        currency="USD",
    )
    assert result.action == NewsAction.TRADE
