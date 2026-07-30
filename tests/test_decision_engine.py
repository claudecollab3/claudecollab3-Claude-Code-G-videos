from datetime import UTC, datetime

from ai.decision import DecisionEngine
from ai.ensemble import EnsembleEngine
from ai.news.policy import NewsAction
from strategies.base import Direction, MarketContext, Signal


class _FakeModel:
    name = "fake"

    def __init__(self, direction: Direction, confidence: float = 80.0):
        self._direction = direction
        self._confidence = confidence

    def predict(self, features):
        from ai.models.base import ModelVote

        probability = 0.5 + (self._confidence / 200) * (
            1 if self._direction == Direction.LONG else -1
        )
        return ModelVote(
            model_name=self.name,
            direction=self._direction,
            probability=probability,
            confidence=self._confidence,
        )


def _signal(direction: Direction = Direction.LONG, confidence: float = 70.0) -> Signal:
    return Signal(
        strategy_name="test_strategy",
        symbol="EURUSD",
        direction=direction,
        entry_price=1.1,
        stop_loss=1.09,
        take_profit=1.12,
        confidence=confidence,
        reasons=["synthetic"],
    )


def _context() -> MarketContext:
    return MarketContext(symbol="EURUSD", timeframes={}, spread_points=5.0)


def test_ai_agreement_blends_confidence():
    ensemble = EnsembleEngine([_FakeModel(Direction.LONG, confidence=90.0)])
    engine = DecisionEngine(ensemble)

    results = engine.evaluate(
        context=_context(),
        strategy_signals=[_signal(Direction.LONG, confidence=70.0)],
        news_events=[],
        news_trading_enabled=False,
        news_blackout_minutes=30,
        now=datetime.now(UTC),
    )

    assert len(results) == 1
    result = results[0]
    assert result.ai_direction_agrees is True
    assert result.signal.confidence > 0
    assert any(item.name == "ai_confirmation" and item.passed for item in result.checklist)


def test_ai_disagreement_zeroes_confidence():
    ensemble = EnsembleEngine([_FakeModel(Direction.SHORT, confidence=90.0)])
    engine = DecisionEngine(ensemble)

    results = engine.evaluate(
        context=_context(),
        strategy_signals=[_signal(Direction.LONG, confidence=70.0)],
        news_events=[],
        news_trading_enabled=False,
        news_blackout_minutes=30,
        now=datetime.now(UTC),
    )

    assert len(results) == 1
    result = results[0]
    assert result.ai_direction_agrees is False
    assert result.signal.confidence == 0.0
    assert any(item.name == "ai_confirmation" and not item.passed for item in result.checklist)


def test_news_blackout_zeroes_confidence_even_if_ai_agrees():
    from datetime import timedelta

    from ai.news.calendar import CalendarEvent, NewsImpact

    ensemble = EnsembleEngine([_FakeModel(Direction.LONG, confidence=90.0)])
    engine = DecisionEngine(ensemble)
    now = datetime.now(UTC)

    event = CalendarEvent(
        external_id="evt",
        name="FOMC",
        currency="EUR",
        impact=NewsImpact.HIGH,
        event_time=now + timedelta(minutes=5),
    )

    results = engine.evaluate(
        context=_context(),
        strategy_signals=[_signal(Direction.LONG, confidence=70.0)],
        news_events=[event],
        news_trading_enabled=False,
        news_blackout_minutes=30,
        now=now,
    )

    assert results[0].news_action != NewsAction.TRADE
    assert results[0].signal.confidence == 0.0
