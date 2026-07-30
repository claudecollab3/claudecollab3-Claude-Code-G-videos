"""Liquidity sweep detection: price wicks beyond a prior swing high/low
(where stop-loss and breakout orders tend to cluster) and then closes back
inside — often read as "smart money" grabbing liquidity before reversing."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from strategies.smc.structure import SwingPoint


@dataclass
class LiquiditySweep:
    timestamp: datetime
    swept_level: float
    bullish: bool  # True = swept a low (liquidity grab before reversing up)


def detect_liquidity_sweeps(df: pd.DataFrame, swings: list[SwingPoint]) -> list[LiquiditySweep]:
    sweeps: list[LiquiditySweep] = []
    swing_highs = [s for s in swings if s.is_high]
    swing_lows = [s for s in swings if not s.is_high]

    for i in range(len(df)):
        ts = df.index[i]
        bar = df.iloc[i]

        for low in swing_lows:
            if low.timestamp >= ts:
                continue
            if bar["low"] < low.price < bar["close"]:
                sweeps.append(LiquiditySweep(timestamp=ts, swept_level=low.price, bullish=True))

        for high in swing_highs:
            if high.timestamp >= ts:
                continue
            if bar["high"] > high.price > bar["close"]:
                sweeps.append(LiquiditySweep(timestamp=ts, swept_level=high.price, bullish=False))

    return sweeps
