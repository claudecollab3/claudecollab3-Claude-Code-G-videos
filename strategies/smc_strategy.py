"""Smart Money Concepts / ICT strategy: combines a recent Change of
Character or Break of Structure with price sitting inside a fresh order
block or fair value gap in the same direction, weighted higher if it lines
up with a kill zone session window."""

from strategies.base import Direction, MarketContext, Signal, Strategy
from strategies.indicators import atr
from strategies.smc.fair_value_gap import detect_fair_value_gaps
from strategies.smc.order_blocks import detect_order_blocks
from strategies.smc.sessions import is_kill_zone
from strategies.smc.structure import StructureEventKind, detect_structure_events


class SmcStrategy(Strategy):
    name = "smc"

    def __init__(
        self, *, swing_lookback: int = 2, atr_period: int = 14, reward_risk_ratio: float = 2.5
    ):
        self.swing_lookback = swing_lookback
        self.atr_period = atr_period
        self.reward_risk_ratio = reward_risk_ratio

    def analyze(self, context: MarketContext) -> Signal | None:
        h1 = context.timeframes.get("H1")
        if h1 is None or len(h1) < 50:
            return None

        events = detect_structure_events(h1, lookback=self.swing_lookback)
        if not events:
            return None
        latest_event = events[-1]

        if latest_event.kind in (StructureEventKind.BOS_BULLISH, StructureEventKind.CHOCH_BULLISH):
            direction = Direction.LONG
        elif latest_event.kind in (
            StructureEventKind.BOS_BEARISH,
            StructureEventKind.CHOCH_BEARISH,
        ):
            direction = Direction.SHORT
        else:
            return None

        price = float(h1["close"].iloc[-1])
        reasons = [f"Latest structure event: {latest_event.kind.value} at {latest_event.price:.5f}"]
        confidence = 60.0
        if latest_event.kind in (
            StructureEventKind.CHOCH_BULLISH,
            StructureEventKind.CHOCH_BEARISH,
        ):
            confidence += 5.0  # a fresh reversal signal is treated as a slightly stronger cue

        order_blocks = detect_order_blocks(h1)
        in_order_block = any(
            ob.bullish == (direction == Direction.LONG) and ob.bottom <= price <= ob.top
            for ob in order_blocks
        )
        if in_order_block:
            confidence += 15.0
            reasons.append("Price sitting inside a same-direction order block")

        fvgs = detect_fair_value_gaps(h1)
        in_fvg = any(
            fvg.bullish == (direction == Direction.LONG) and fvg.bottom <= price <= fvg.top
            for fvg in fvgs
        )
        if in_fvg:
            confidence += 10.0
            reasons.append("Price sitting inside a same-direction fair value gap")

        if not in_order_block and not in_fvg:
            return None  # structure alone isn't enough; require a confluence zone

        if is_kill_zone(h1.index[-1]):
            confidence += 10.0
            reasons.append("Inside a London/New York kill zone")

        atr_value = float(atr(h1, self.atr_period).iloc[-1])
        if atr_value != atr_value:  # NaN
            return None

        stop_loss = price - atr_value if direction == Direction.LONG else price + atr_value
        take_profit = (
            price + atr_value * self.reward_risk_ratio
            if direction == Direction.LONG
            else price - atr_value * self.reward_risk_ratio
        )

        return Signal(
            strategy_name=self.name,
            symbol=context.symbol,
            direction=direction,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=min(95.0, confidence),
            reasons=reasons,
        )
