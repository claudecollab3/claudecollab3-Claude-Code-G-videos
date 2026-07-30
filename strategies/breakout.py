"""Breakout strategy: price closes beyond the strongest nearby support/
resistance level (clustered from swing points) with a volume spike
confirming genuine participation rather than a low-liquidity poke."""

from strategies.base import Direction, MarketContext, Signal, Strategy
from strategies.indicators import atr
from strategies.market_conditions import is_volume_spike
from strategies.smc.levels import cluster_levels
from strategies.smc.structure import find_swing_points


class BreakoutStrategy(Strategy):
    name = "breakout"

    def __init__(
        self,
        *,
        swing_lookback: int = 2,
        level_tolerance_pct: float = 0.0015,
        atr_period: int = 14,
        stop_atr_multiple: float = 1.2,
        reward_risk_ratio: float = 2.0,
    ):
        self.swing_lookback = swing_lookback
        self.level_tolerance_pct = level_tolerance_pct
        self.atr_period = atr_period
        self.stop_atr_multiple = stop_atr_multiple
        self.reward_risk_ratio = reward_risk_ratio

    def analyze(self, context: MarketContext) -> Signal | None:
        h1 = context.timeframes.get("H1")
        if h1 is None or len(h1) < 50:
            return None

        swings = find_swing_points(h1, lookback=self.swing_lookback)
        if not swings:
            return None
        levels = cluster_levels(swings, tolerance_pct=self.level_tolerance_pct)
        if not levels:
            return None

        price = float(h1["close"].iloc[-1])
        prev_price = float(h1["close"].iloc[-2])
        atr_value = float(atr(h1, self.atr_period).iloc[-1])
        if atr_value != atr_value:  # NaN
            return None

        volume_confirmed = is_volume_spike(h1)

        direction: Direction | None = None
        broken_level = None
        for level in levels:
            if level.is_resistance and prev_price <= level.price < price:
                direction = Direction.LONG
                broken_level = level
                break
            if not level.is_resistance and prev_price >= level.price > price:
                direction = Direction.SHORT
                broken_level = level
                break

        if direction is None or broken_level is None:
            return None
        if not volume_confirmed:
            return None

        reasons = [
            f"Closed through {'resistance' if broken_level.is_resistance else 'support'} "
            f"at {broken_level.price:.5f} ({broken_level.touches} prior touches)",
            "Volume spike confirms the breakout",
        ]
        confidence = min(90.0, 55.0 + broken_level.touches * 5)

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
