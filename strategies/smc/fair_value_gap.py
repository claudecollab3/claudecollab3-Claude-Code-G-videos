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
    gaps: list[FairValueGap] = []

    for i in range(2, len(df)):
        first, third = df.iloc[i - 2], df.iloc[i]

        if first["high"] < third["low"]:
            gaps.append(
                FairValueGap(
                    timestamp=df.index[i - 1],
                    top=float(third["low"]),
                    bottom=float(first["high"]),
                    bullish=True,
                )
            )
        elif first["low"] > third["high"]:
            gaps.append(
                FairValueGap(
                    timestamp=df.index[i - 1],
                    top=float(first["low"]),
                    bottom=float(third["high"]),
                    bullish=False,
                )
            )

    return gaps
