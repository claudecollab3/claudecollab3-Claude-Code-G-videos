"""Spread/slippage ceilings and post-entry trade management rules
(break-even, trailing stop, partial close)."""

from dataclasses import dataclass


def spread_within_limit(current_spread_points: float, max_spread_points: float) -> bool:
    return current_spread_points <= max_spread_points


def slippage_within_limit(
    expected_price: float, filled_price: float, point_size: float, max_slippage_points: float
) -> bool:
    slippage_points = abs(filled_price - expected_price) / point_size
    return slippage_points <= max_slippage_points


@dataclass
class TrailingStopResult:
    new_stop_loss: float
    moved: bool


def compute_break_even_stop(
    *,
    entry_price: float,
    current_price: float,
    is_long: bool,
    trigger_rr: float,
    stop_loss: float,
) -> float | None:
    """Once price has moved `trigger_rr` times the original risk in favor,
    move the stop to entry (break-even). Returns None if not yet triggered."""
    original_risk = abs(entry_price - stop_loss)
    if original_risk <= 0:
        return None

    progressed = (current_price - entry_price) if is_long else (entry_price - current_price)
    if progressed >= trigger_rr * original_risk:
        return entry_price
    return None


def compute_trailing_stop(
    *, current_price: float, current_stop_loss: float, is_long: bool, trail_distance: float
) -> TrailingStopResult:
    if is_long:
        candidate = current_price - trail_distance
        if candidate > current_stop_loss:
            return TrailingStopResult(new_stop_loss=candidate, moved=True)
    else:
        candidate = current_price + trail_distance
        if candidate < current_stop_loss:
            return TrailingStopResult(new_stop_loss=candidate, moved=True)

    return TrailingStopResult(new_stop_loss=current_stop_loss, moved=False)


def partial_close_volume(
    position_volume: float, partial_close_percent: float, *, min_lot: float = 0.01
) -> float:
    volume = round(position_volume * (partial_close_percent / 100), 2)
    return volume if volume >= min_lot else 0.0
