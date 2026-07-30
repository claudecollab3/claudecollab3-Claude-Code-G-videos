"""Break of Structure (BOS) and Change of Character (CHoCH) detection via
swing high/low pivots — the foundational Smart Money Concepts building
block the other detectors (order blocks, liquidity sweeps, levels) key off.

Note: BOS/CHoCH is an inherently discretionary concept in SMC/ICT trading
with no single canonical formal definition. This is a documented, simplified
heuristic (fractal swing pivots + same-direction/opposite-direction breaks),
not an attempt to codify "the" official rule set.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import pandas as pd


class StructureEventKind(str, Enum):
    BOS_BULLISH = "bos_bullish"
    BOS_BEARISH = "bos_bearish"
    CHOCH_BULLISH = "choch_bullish"
    CHOCH_BEARISH = "choch_bearish"


@dataclass
class SwingPoint:
    timestamp: datetime
    price: float
    is_high: bool


@dataclass
class StructureEvent:
    timestamp: datetime
    kind: StructureEventKind
    price: float


def find_swing_points(df: pd.DataFrame, lookback: int = 2) -> list[SwingPoint]:
    """A bar is a confirmed swing high/low if it's the strict max/min within
    `lookback` bars on both sides (a simple fractal pivot definition)."""
    points: list[SwingPoint] = []
    highs, lows = df["high"], df["low"]
    n = len(df)

    for i in range(lookback, n - lookback):
        window_high = highs.iloc[i - lookback : i + lookback + 1]
        window_low = lows.iloc[i - lookback : i + lookback + 1]

        if highs.iloc[i] == window_high.max() and (window_high == window_high.max()).sum() == 1:
            points.append(
                SwingPoint(timestamp=df.index[i], price=float(highs.iloc[i]), is_high=True)
            )
        if lows.iloc[i] == window_low.min() and (window_low == window_low.min()).sum() == 1:
            points.append(
                SwingPoint(timestamp=df.index[i], price=float(lows.iloc[i]), is_high=False)
            )

    return sorted(points, key=lambda p: p.timestamp)


def detect_structure_events(df: pd.DataFrame, lookback: int = 2) -> list[StructureEvent]:
    """Walks confirmed swing points in order, tracking the prevailing trend.

    A break beyond the last same-type swing in the trend's own direction is
    a BOS (continuation); a break in the opposite direction of the
    prevailing trend is a CHoCH (the first signal of a potential reversal).
    """
    swings = find_swing_points(df, lookback=lookback)
    events: list[StructureEvent] = []

    trend: int | None = None  # 1 = up, -1 = down; seeded from the first directional break
    last_swing_high: SwingPoint | None = None
    last_swing_low: SwingPoint | None = None

    for point in swings:
        if point.is_high:
            if last_swing_high is not None:
                if point.price > last_swing_high.price:
                    if trend is None:
                        trend = 1  # first higher-high we see seeds an uptrend
                    elif trend == -1:
                        events.append(
                            StructureEvent(
                                point.timestamp, StructureEventKind.CHOCH_BULLISH, point.price
                            )
                        )
                        trend = 1
                    else:
                        events.append(
                            StructureEvent(
                                point.timestamp, StructureEventKind.BOS_BULLISH, point.price
                            )
                        )
                elif trend is None:
                    trend = -1  # first lower-high we see seeds a downtrend
            last_swing_high = point
        else:
            if last_swing_low is not None:
                if point.price < last_swing_low.price:
                    if trend is None:
                        trend = -1  # first lower-low we see seeds a downtrend
                    elif trend == 1:
                        events.append(
                            StructureEvent(
                                point.timestamp, StructureEventKind.CHOCH_BEARISH, point.price
                            )
                        )
                        trend = -1
                    else:
                        events.append(
                            StructureEvent(
                                point.timestamp, StructureEventKind.BOS_BEARISH, point.price
                            )
                        )
                elif trend is None:
                    trend = 1  # first higher-low we see seeds an uptrend
            last_swing_low = point

    return events
