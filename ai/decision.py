"""Decision & Confidence Engine: combines strategy signals, the AI
ensemble's independent prediction, and the news policy into one final,
explainable decision per symbol — the "AI CONFIRMATION" checklist from the
spec (trend/strategy confidence, AI confirmation, news) rolled into a
single call.

Spread, position sizing, and account-protection limits are the
RiskManager's job (Phase 4); this engine's output is exactly the `Signal`
type RiskManager already expects, plus a checklist explaining why AI
confirmed or rejected each strategy signal. A signal whose direction the AI
ensemble disagrees with, or that falls inside a news blackout, comes out
with confidence forced to 0 so RiskManager's confidence-threshold check
rejects it the same way any other low-confidence signal would — one
funnel, not two.
"""

from dataclasses import dataclass, replace
from datetime import datetime

from ai.ensemble import EnsembleEngine
from ai.features import build_feature_vector
from ai.news.calendar import CalendarEvent
from ai.news.policy import NewsAction, NewsPolicy
from strategies.base import MarketContext, Signal


@dataclass
class ChecklistItem:
    name: str
    passed: bool
    detail: str


@dataclass
class ConfirmedSignal:
    signal: Signal
    checklist: list[ChecklistItem]
    ai_direction_agrees: bool
    news_action: NewsAction


class DecisionEngine:
    def __init__(self, ensemble: EnsembleEngine, news_policy: NewsPolicy | None = None):
        self._ensemble = ensemble
        self._news_policy = news_policy or NewsPolicy()

    def evaluate(
        self,
        *,
        context: MarketContext,
        strategy_signals: list[Signal],
        news_events: list[CalendarEvent],
        news_trading_enabled: bool,
        news_blackout_minutes: int,
        now: datetime,
    ) -> list[ConfirmedSignal]:
        features = build_feature_vector(context)
        ai_result = self._ensemble.predict(features)

        news_result = self._news_policy.evaluate(
            events=news_events,
            now=now,
            news_trading_enabled=news_trading_enabled,
            blackout_minutes=news_blackout_minutes,
            currency=context.symbol[:3],  # e.g. EURUSD -> EUR; a coarse heuristic
        )
        news_clear = news_result.action == NewsAction.TRADE

        confirmed: list[ConfirmedSignal] = []
        for signal in strategy_signals:
            ai_agrees = ai_result.direction == signal.direction

            checklist = [
                ChecklistItem(
                    "strategy_confidence", signal.confidence > 0, f"{signal.confidence:.1f}%"
                ),
                ChecklistItem(
                    "ai_confirmation",
                    ai_agrees,
                    f"AI predicts {ai_result.direction.value} at {ai_result.confidence:.1f}% "
                    f"vs strategy {signal.direction.value}",
                ),
                ChecklistItem("news", news_clear, news_result.reason),
            ]

            if not ai_agrees or not news_clear:
                confirmed.append(
                    ConfirmedSignal(
                        signal=replace(signal, confidence=0.0),
                        checklist=checklist,
                        ai_direction_agrees=ai_agrees,
                        news_action=news_result.action,
                    )
                )
                continue

            blended_confidence = min(100.0, (signal.confidence + ai_result.confidence) / 2)
            confirmed.append(
                ConfirmedSignal(
                    signal=replace(
                        signal,
                        confidence=blended_confidence,
                        reasons=[
                            *signal.reasons,
                            f"AI ensemble agrees ({ai_result.confidence:.1f}%)",
                        ],
                    ),
                    checklist=checklist,
                    ai_direction_agrees=True,
                    news_action=news_result.action,
                )
            )

        return confirmed
