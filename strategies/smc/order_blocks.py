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
    atr_series = _atr(df, atr_period)
    blocks: list[OrderBlock] = []

    for i in range(1, len(df)):
        threshold = atr_series.iloc[i]
        if pd.isna(threshold) or threshold == 0:
            continue

        body = df["close"].iloc[i] - df["open"].iloc[i]
        prev = df.iloc[i - 1]

        if body > displacement_atr_multiple * threshold and prev["close"] < prev["open"]:
            blocks.append(
                OrderBlock(
                    timestamp=df.index[i - 1],
                    top=float(prev["open"]),
                    bottom=float(prev["close"]),
                    bullish=True,
                )
            )
        elif body < -displacement_atr_multiple * threshold and prev["close"] > prev["open"]:
            blocks.append(
                OrderBlock(
                    timestamp=df.index[i - 1],
                    top=float(prev["close"]),
                    bottom=float(prev["open"]),
                    bullish=False,
                )
            )

    return blocks
