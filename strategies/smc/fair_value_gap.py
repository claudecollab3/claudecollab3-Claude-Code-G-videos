"""Fair Value Gap (FVG) detection: a 3-candle imbalance where the first
candle's high/low doesn't overlap the third candle's low/high, leaving a
price gap the market often later returns to "fill"."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class FairValueGap:
    timestamp: datetime  # timestamp of the middle (displacement) candle
    top: float
    bottom: float
    bullish: bool


def detect_fair_value_gaps(df: pd.DataFrame) -> list[FairValueGap]:
    """Vectorized: per-bar `.iloc` slicing in a Python loop was slow enough,
    called once per bar of a walk-forward backtest, to make a full replay
    take minutes (see backtesting/README.md's performance note)."""
    n = len(df)
    if n <= 2:
        return []

    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    mid_timestamps = df.index[1:-1]
    first_high, first_low = highs[:-2], lows[:-2]
    third_high, third_low = highs[2:], lows[2:]

    bullish_mask = first_high < third_low
    bearish_mask = (first_low > third_high) & ~bullish_mask  # if/elif precedence

    gaps = [
        FairValueGap(timestamp=ts, top=float(tl), bottom=float(fh), bullish=True)
        for ts, fh, tl, flag in zip(
            mid_timestamps, first_high, third_low, bullish_mask, strict=True
        )
        if flag
    ]
    gaps.extend(
        FairValueGap(timestamp=ts, top=float(fl), bottom=float(th), bullish=False)
        for ts, fl, th, flag in zip(
            mid_timestamps, first_low, third_high, bearish_mask, strict=True
        )
        if flag
    )
    return gaps
