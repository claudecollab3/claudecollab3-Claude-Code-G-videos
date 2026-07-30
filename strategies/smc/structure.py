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
    `lookback` bars on both sides (a simple fractal pivot definition).

    Being the *unique* max/min of a `2*lookback+1`-wide window is equivalent
    to being strictly greater/less than every other bar in that window, so
    this is computed with vectorized shift-and-compare rather than a
    per-bar Python loop with `.iloc` window slicing — the latter was slow
    enough (one call per bar, each looking back over the whole window) to
    make a full walk-forward backtest replay effectively hang.
    """
    highs, lows = df["high"], df["low"]
    if len(df) <= 2 * lookback:
        return []

    is_high = pd.Series(True, index=df.index)
    is_low = pd.Series(True, index=df.index)
    for offset in range(1, lookback + 1):
        is_high &= (highs > highs.shift(offset)) & (highs > highs.shift(-offset))
        is_low &= (lows < lows.shift(offset)) & (lows < lows.shift(-offset))

    points = [
        SwingPoint(timestamp=ts, price=float(price), is_high=True)
        for ts, price, flag in zip(df.index, highs, is_high, strict=True)
        if flag
    ]
    points.extend(
        SwingPoint(timestamp=ts, price=float(price), is_high=False)
        for ts, price, flag in zip(df.index, lows, is_low, strict=True)
        if flag
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
