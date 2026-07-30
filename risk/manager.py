"""RiskManager: the single gate every proposed trade passes through before
execution. Combines account-protection limits, position sizing, and
spread/confidence filters into one approve/reject decision with a
human-readable reason — regardless of which strategy or AI model produced
the signal."""

from dataclasses import dataclass

from risk.guards import spread_within_limit
from risk.limits import (
    AccountState,
    RiskLimits,
    daily_loss_percent,
    drawdown_percent,
    weekly_loss_percent,
)
from risk.position_sizing import calculate_position_size
from strategies.base import Signal


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    volume: float = 0.0
    risk_amount: float = 0.0


class RiskManager:
    def __init__(self, limits: RiskLimits):
        self.limits = limits

    def evaluate(
        self,
        *,
        signal: Signal,
        account: AccountState,
        current_spread_points: float,
        pip_value_per_lot: float = 10.0,
        pip_size: float = 0.0001,
        min_lot: float = 0.01,
        max_lot: float = 100.0,
    ) -> RiskDecision:
        if account.emergency_stop:
            return RiskDecision(approved=False, reason="Emergency stop is active")

        if signal.confidence < self.limits.confidence_threshold:
            return RiskDecision(
                approved=False,
                reason=(
                    f"Confidence {signal.confidence:.1f}% is below the configured threshold "
                    f"of {self.limits.confidence_threshold:.1f}%"
                ),
            )

        if not spread_within_limit(current_spread_points, self.limits.max_spread_points):
            return RiskDecision(
                approved=False,
                reason=f"Spread {current_spread_points} exceeds max allowed {self.limits.max_spread_points}",
            )

        if account.open_positions_count >= self.limits.max_open_positions:
            return RiskDecision(approved=False, reason="Max open positions limit reached")

        if account.trades_today >= self.limits.max_trades_per_day:
            return RiskDecision(approved=False, reason="Max trades per day limit reached")

        if daily_loss_percent(account) >= self.limits.max_daily_loss_percent:
            return RiskDecision(approved=False, reason="Daily loss limit reached")

        if weekly_loss_percent(account) >= self.limits.max_weekly_loss_percent:
            return RiskDecision(approved=False, reason="Weekly loss limit reached")

        if drawdown_percent(account) >= self.limits.max_drawdown_percent:
            return RiskDecision(approved=False, reason="Max drawdown limit reached")

        sizing = calculate_position_size(
            account_balance=account.balance,
            risk_per_trade_percent=self.limits.risk_per_trade_percent,
            entry_price=signal.entry_price,
            stop_loss_price=signal.stop_loss,
            pip_value_per_lot=pip_value_per_lot,
            pip_size=pip_size,
            min_lot=min_lot,
            max_lot=max_lot,
        )
        if not sizing.viable:
            return RiskDecision(approved=False, reason=sizing.warning or "Position size not viable")

        return RiskDecision(
            approved=True, reason="approved", volume=sizing.volume, risk_amount=sizing.risk_amount
        )
