"""Hard account-protection limits: daily/weekly loss, drawdown, trade/
position caps, emergency stop. These feed the risk manager's non-negotiable
gates — no strategy or AI confidence can override them."""

from dataclasses import dataclass


@dataclass
class AccountState:
    balance: float
    equity: float
    starting_balance_today: float
    starting_balance_this_week: float
    peak_equity: float
    open_positions_count: int = 0
    trades_today: int = 0
    emergency_stop: bool = False


@dataclass
class RiskLimits:
    risk_per_trade_percent: float
    max_daily_loss_percent: float
    max_weekly_loss_percent: float
    max_drawdown_percent: float
    max_open_positions: int
    max_trades_per_day: int
    max_spread_points: float
    max_slippage_points: float
    daily_profit_target_percent: float
    confidence_threshold: float


def daily_loss_percent(state: AccountState) -> float:
    if state.starting_balance_today <= 0:
        return 0.0
    return max(
        0.0, (state.starting_balance_today - state.equity) / state.starting_balance_today * 100
    )


def weekly_loss_percent(state: AccountState) -> float:
    if state.starting_balance_this_week <= 0:
        return 0.0
    return max(
        0.0,
        (state.starting_balance_this_week - state.equity) / state.starting_balance_this_week * 100,
    )


def drawdown_percent(state: AccountState) -> float:
    if state.peak_equity <= 0:
        return 0.0
    return max(0.0, (state.peak_equity - state.equity) / state.peak_equity * 100)


def daily_profit_percent(state: AccountState) -> float:
    if state.starting_balance_today <= 0:
        return 0.0
    return max(
        0.0, (state.equity - state.starting_balance_today) / state.starting_balance_today * 100
    )
