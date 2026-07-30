"""Trend-following strategy: EMA(50)/EMA(200) crossover on H1, confirmed by
ADX strength on H1 and higher-timeframe (H4) trend alignment — the "combine
multiple timeframe confirmations before entering a trade" requirement."""

import math

from strategies.base import Direction, MarketContext, Signal, Strategy
from strategies.indicators import adx, atr, ema


class TrendFollowingStrategy(Strategy):
    name = "trend_following"

    def __init__(
        self,
        *,
        fast_period: int = 50,
        slow_period: int = 200,
        adx_period: int = 14,
        adx_threshold: float = 20.0,
        atr_period: int = 14,
        stop_atr_multiple: float = 1.5,
        reward_risk_ratio: float = 2.0,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.atr_period = atr_period
        self.stop_atr_multiple = stop_atr_multiple
        self.reward_risk_ratio = reward_risk_ratio

    def analyze(self, context: MarketContext) -> Signal | None:
        h1 = context.timeframes.get("H1")
        h4 = context.timeframes.get("H4")
        if h1 is None or h4 is None:
            return None
        if len(h1) < self.slow_period + 1 or len(h4) < self.slow_period + 1:
            return None

        fast_h1 = ema(h1["close"], self.fast_period)
        slow_h1 = ema(h1["close"], self.slow_period)
        fast_h4 = ema(h4["close"], self.fast_period)
        slow_h4 = ema(h4["close"], self.slow_period)
        adx_h1 = adx(h1, self.adx_period)
        atr_h1 = atr(h1, self.atr_period)

        latest_values = [
            fast_h1.iloc[-1],
            slow_h1.iloc[-1],
            fast_h4.iloc[-1],
            slow_h4.iloc[-1],
            adx_h1.iloc[-1],
            atr_h1.iloc[-1],
        ]
        if any(math.isnan(v) for v in latest_values):
            return None

        price = float(h1["close"].iloc[-1])
        h1_bullish = fast_h1.iloc[-1] > slow_h1.iloc[-1]
        h4_bullish = fast_h4.iloc[-1] > slow_h4.iloc[-1]
        trend_strength = float(adx_h1.iloc[-1])
        atr_value = float(atr_h1.iloc[-1])

        if trend_strength < self.adx_threshold:
            return None
        if h1_bullish != h4_bullish:
            return None  # no higher-timeframe alignment

        reasons = [
            f"H1 EMA{self.fast_period}/EMA{self.slow_period} crossover "
            f"{'bullish' if h1_bullish else 'bearish'}",
            f"H4 trend aligned ({'bullish' if h4_bullish else 'bearish'})",
            f"ADX(H1)={trend_strength:.1f} >= {self.adx_threshold}",
        ]
        confidence = min(95.0, 55.0 + (trend_strength - self.adx_threshold))

        stop_distance = atr_value * self.stop_atr_multiple
        direction = Direction.LONG if h1_bullish else Direction.SHORT
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
