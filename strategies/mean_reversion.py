"""Mean-reversion strategy: price tags a Bollinger Band extreme while RSI
confirms an overbought/oversold reading on M15."""

import math

from strategies.base import Direction, MarketContext, Signal, Strategy
from strategies.indicators import atr, bollinger_bands, rsi


class MeanReversionStrategy(Strategy):
    name = "mean_reversion"

    def __init__(
        self,
        *,
        bb_period: int = 20,
        bb_std_dev: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        atr_period: int = 14,
        stop_atr_multiple: float = 1.0,
        reward_risk_ratio: float = 1.5,
    ):
        self.bb_period = bb_period
        self.bb_std_dev = bb_std_dev
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.atr_period = atr_period
        self.stop_atr_multiple = stop_atr_multiple
        self.reward_risk_ratio = reward_risk_ratio

    def analyze(self, context: MarketContext) -> Signal | None:
        m15 = context.timeframes.get("M15")
        if m15 is None or len(m15) < self.bb_period + 1:
            return None

        upper, mid, lower = bollinger_bands(m15["close"], self.bb_period, self.bb_std_dev)
        rsi_series = rsi(m15["close"], self.rsi_period)
        atr_series = atr(m15, self.atr_period)

        latest = [
            upper.iloc[-1],
            mid.iloc[-1],
            lower.iloc[-1],
            rsi_series.iloc[-1],
            atr_series.iloc[-1],
        ]
        if any(math.isnan(v) for v in latest):
            return None

        price = float(m15["close"].iloc[-1])
        rsi_value = float(rsi_series.iloc[-1])
        atr_value = float(atr_series.iloc[-1])

        direction: Direction | None = None
        reasons: list[str] = []

        if price <= lower.iloc[-1] and rsi_value <= self.rsi_oversold:
            direction = Direction.LONG
            reasons = [
                f"Price at/below lower Bollinger Band ({price:.5f} <= {lower.iloc[-1]:.5f})",
                f"RSI({self.rsi_period})={rsi_value:.1f} <= {self.rsi_oversold} (oversold)",
            ]
        elif price >= upper.iloc[-1] and rsi_value >= self.rsi_overbought:
            direction = Direction.SHORT
            reasons = [
                f"Price at/above upper Bollinger Band ({price:.5f} >= {upper.iloc[-1]:.5f})",
                f"RSI({self.rsi_period})={rsi_value:.1f} >= {self.rsi_overbought} (overbought)",
            ]

        if direction is None:
            return None

        extremity = abs(rsi_value - 50) - (50 - min(self.rsi_oversold, 100 - self.rsi_overbought))
        confidence = min(90.0, 60.0 + max(0.0, extremity))

        stop_distance = atr_value * self.stop_atr_multiple
        stop_loss = price - stop_distance if direction == Direction.LONG else price + stop_distance
        take_profit = (
            price + stop_distance * self.reward_risk_ratio
            if direction == Direction.LONG
            else price - stop_distance * self.reward_risk_ratio
        )

        return Signal(
            strategy_name=self.name,
            symbol=context.symbol,
            direction=direction,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            reasons=reasons,
        )
