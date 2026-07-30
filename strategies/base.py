"""Common strategy interface.

Every strategy (SMC/ICT, price action, indicator-based, etc.) implements this
interface so the strategy engine can enable/disable and combine them
uniformly. Full detector implementations land in Phase 4.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class MarketContext:
    """Snapshot of everything a strategy needs to evaluate a symbol."""

    symbol: str
    timeframes: dict  # e.g. {"M1": DataFrame, "M5": DataFrame, ...}
    spread_points: float
    session: str | None = None
    news_blackout: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class Signal:
    """A candidate trade idea produced by a strategy or the AI ensemble."""

    strategy_name: str
    symbol: str
    direction: Direction
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float  # 0-100, populated/refined by the decision engine
    reasons: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


class Strategy(ABC):
    """Base class every trading strategy must implement."""

    name: str = "base"
    enabled: bool = True

    @abstractmethod
    def analyze(self, context: MarketContext) -> Signal | None:
        """Return a Signal if this strategy sees a valid setup, else None."""
        raise NotImplementedError
