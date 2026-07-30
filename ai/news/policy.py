"""Decides Trade / Wait / Reduce risk / Close existing based on upcoming
high-impact news, and produces the human-readable reason the spec's
"High Impact News in 10 minutes." / "Trading paused." notifications are
built from (actual dispatch to Telegram/Discord/email is `notifications/`,
Phase 7 — this module only decides *what* to say and *what* to do).
"""

import enum
from dataclasses import dataclass
from datetime import datetime

from ai.news.calendar import CalendarEvent, NewsImpact


class NewsAction(str, enum.Enum):
    TRADE = "trade"
    WAIT = "wait"
    REDUCE_RISK = "reduce_risk"
    CLOSE_EXISTING = "close_existing"


@dataclass
class NewsPolicyResult:
    action: NewsAction
    reason: str
    upcoming_event: CalendarEvent | None = None


class NewsPolicy:
    def evaluate(
        self,
        *,
        events: list[CalendarEvent],
        now: datetime,
        news_trading_enabled: bool,
        blackout_minutes: int,
        currency: str | None = None,
    ) -> NewsPolicyResult:
        relevant = [
            e
            for e in events
            if e.impact == NewsImpact.HIGH
            and (currency is None or e.currency.upper() == currency.upper())
        ]
        if not relevant:
            return NewsPolicyResult(action=NewsAction.TRADE, reason="No high-impact news in range")

        if news_trading_enabled:
            return NewsPolicyResult(
                action=NewsAction.TRADE,
                reason="News trading is enabled by user configuration",
                upcoming_event=relevant[0],
            )

        upcoming = min(relevant, key=lambda e: abs((e.event_time - now).total_seconds()))
        minutes_to_event = (upcoming.event_time - now).total_seconds() / 60

        if 0 <= minutes_to_event <= blackout_minutes:
            # Closer to the event = more caution: get flat, don't just size down.
            action = (
                NewsAction.CLOSE_EXISTING
                if minutes_to_event <= blackout_minutes / 3
                else NewsAction.REDUCE_RISK
            )
            return NewsPolicyResult(
                action=action,
                reason=f"High-impact news '{upcoming.name}' in {minutes_to_event:.0f} minutes",
                upcoming_event=upcoming,
            )

        if -blackout_minutes <= minutes_to_event < 0:
            return NewsPolicyResult(
                action=NewsAction.WAIT,
                reason=f"High-impact news '{upcoming.name}' released {abs(minutes_to_event):.0f} minutes ago",
                upcoming_event=upcoming,
            )

        return NewsPolicyResult(
            action=NewsAction.TRADE, reason="No high-impact news within the blackout window"
        )
