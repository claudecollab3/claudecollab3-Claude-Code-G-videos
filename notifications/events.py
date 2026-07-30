"""Notification event types and the message payload every channel sends."""

import enum
from dataclasses import dataclass, field
from typing import Any


class NotificationEvent(str, enum.Enum):
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    TAKE_PROFIT_HIT = "take_profit_hit"
    STOP_LOSS_HIT = "stop_loss_hit"
    HIGH_IMPACT_NEWS = "high_impact_news"
    TRADING_PAUSED = "trading_paused"
    BROKER_DISCONNECTED = "broker_disconnected"
    LARGE_DRAWDOWN = "large_drawdown"
    DAILY_GOAL_REACHED = "daily_goal_reached"


@dataclass
class NotificationMessage:
    event: NotificationEvent
    title: str
    body: str
    data: dict[str, Any] = field(default_factory=dict)
