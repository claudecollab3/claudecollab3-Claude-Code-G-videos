"""Order block detection: the last opposite-direction candle before a
strong displacement move, treated as a zone where "smart money" orders may
still be resting and price may return to react from."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from strategies.indicators import atr as _atr


@dataclass
class OrderBlock:
    timestamp: datetime
    top: float
    bottom: float
    bullish: bool  # True = demand zone (expect a bounce up), False = supply zone


def detect_order_blocks(
    df: pd.DataFrame, *, displacement_atr_multiple: float = 1.5, atr_period: int = 14
) -> list[OrderBlock]:
    """Vectorized: per-bar `.iloc` slicing in a Python loop was slow enough,
    called once per bar of a walk-forward backtest, to make a full replay
    take minutes (see backtesting/README.md's performance note)."""
    n = len(df)
    if n <= 1:
        return []

    atr_values = _atr(df, atr_period).to_numpy()
    close, open_ = df["close"].to_numpy(), df["open"].to_numpy()

    body = close[1:] - open_[1:]
    threshold = atr_values[1:]
    prev_close, prev_open = close[:-1], open_[:-1]
    prev_timestamps = df.index[:-1]

    valid = ~pd.isna(threshold) & (threshold != 0)
    bullish_mask = valid & (body > displacement_atr_multiple * threshold) & (prev_close < prev_open)
    bearish_mask = (
        valid & (body < -displacement_atr_multiple * threshold) & (prev_close > prev_open)
    )

    blocks = [
        OrderBlock(timestamp=ts, top=float(po), bottom=float(pc), bullish=True)
        for ts, po, pc, flag in zip(
            prev_timestamps, prev_open, prev_close, bullish_mask, strict=True
        )
        if flag
    ]
    blocks.extend(
        OrderBlock(timestamp=ts, top=float(pc), bottom=float(po), bullish=False)
        for ts, po, pc, flag in zip(
            prev_timestamps, prev_open, prev_close, bearish_mask, strict=True
        )
        if flag
    )
    return blocks
