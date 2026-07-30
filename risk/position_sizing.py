"""Risk-per-trade -> position size, with broker/account-size viability
checks so a tiny account is never silently forced into an oversized
position — the user is warned instead."""

from dataclasses import dataclass


@dataclass
class PositionSizeResult:
    volume: float
    risk_amount: float
    viable: bool
    warning: str | None = None


def calculate_position_size(
    *,
    account_balance: float,
    risk_per_trade_percent: float,
    entry_price: float,
    stop_loss_price: float,
    pip_value_per_lot: float = 10.0,
    pip_size: float = 0.0001,
    min_lot: float = 0.01,
    max_lot: float = 100.0,
    lot_step: float = 0.01,
) -> PositionSizeResult:
    risk_amount = account_balance * (risk_per_trade_percent / 100)
    stop_distance = abs(entry_price - stop_loss_price)

    if stop_distance <= 0:
        return PositionSizeResult(
            volume=0.0, risk_amount=risk_amount, viable=False, warning="Stop loss distance is zero"
        )

    stop_distance_pips = stop_distance / pip_size
    if stop_distance_pips <= 0 or pip_value_per_lot <= 0:
        return PositionSizeResult(
            volume=0.0, risk_amount=risk_amount, viable=False, warning="Invalid pip configuration"
        )

    raw_volume = risk_amount / (stop_distance_pips * pip_value_per_lot)

    if raw_volume < min_lot:
        return PositionSizeResult(
            volume=0.0,
            risk_amount=risk_amount,
            viable=False,
            warning=(
                f"Calculated size ({raw_volume:.4f} lots) is below the broker's minimum lot "
                f"({min_lot}); this account/risk-% combination is too small to trade this "
                "instrument safely at the configured stop distance."
            ),
        )

    volume = min(round(raw_volume / lot_step) * lot_step, max_lot)
    return PositionSizeResult(volume=round(volume, 2), risk_amount=risk_amount, viable=True)
