"""Backtest engine: replays historical OHLCV bars through the exact same
strategy engine and risk manager used live (see docs/ARCHITECTURE.md's
"one code path for backtest and live" principle) — only the data source
(historical `Candle` rows instead of a live `BrokerAdapter`) and the fill
simulation differ.

Simplifications, documented rather than hidden:
- Entries fill at the signal bar's own close (the standard bar-close
  backtest convention), not a following bar's open.
- Exits are detected by scanning forward bars' high/low against the
  stop-loss/take-profit; if a single bar's range would touch both, the
  stop-loss is assumed to hit first — the conservative assumption.
- `equity` tracks realized balance only; open positions are not marked to
  market intrabar. That realized `equity` is what feeds RiskManager's
  daily/weekly loss and drawdown checks during the backtest, same as it
  would from a live account snapshot.
- Each bar's strategy context is a bounded trailing window
  (`config.context_lookback_bars`), not the full history-to-date. An
  earlier version re-sliced the *entire* history every bar; since
  `strategies.smc.structure.find_swing_points` does an O(window) Python
  scan per call, that made the whole backtest O(n^2) in the candle count —
  confirmed to hang the server on a real dataset. Bounding the window
  keeps each bar's work constant, so the full backtest is O(n).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from database.models.market_data import Candle, Timeframe
from risk.limits import AccountState, RiskLimits
from risk.manager import RiskManager
from strategies.base import Direction, MarketContext, Strategy
from strategies.data import candles_to_dataframe
from strategies.registry import run_strategies


@dataclass
class BacktestConfig:
    symbol: str
    primary_timeframe: Timeframe
    risk_limits: RiskLimits
    starting_balance: float = 10_000.0
    spread_points: float = 10.0
    pip_value_per_lot: float = 10.0
    pip_size: float = 0.0001
    min_lot: float = 0.01
    max_lot: float = 100.0
    min_history_bars: int = 60
    context_lookback_bars: int = 500


@dataclass
class OpenPosition:
    position_id: str
    strategy_name: str
    direction: Direction
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    volume: float
    risk_amount: float


@dataclass
class BacktestTrade:
    strategy_name: str
    symbol: str
    direction: Direction
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    stop_loss: float
    take_profit: float
    volume: float
    pnl: float
    r_multiple: float
    exit_reason: str  # "stop_loss" | "take_profit" | "end_of_data"


@dataclass
class BacktestResult:
    trades: list[BacktestTrade]
    equity_curve: list[tuple[datetime, float]]
    starting_balance: float
    ending_balance: float
    rejected_signal_count: int = field(default=0)


def _pnl(
    direction: Direction,
    entry_price: float,
    exit_price: float,
    volume: float,
    config: BacktestConfig,
) -> float:
    direction_sign = 1 if direction == Direction.LONG else -1
    price_diff_pips = direction_sign * (exit_price - entry_price) / config.pip_size
    return price_diff_pips * config.pip_value_per_lot * volume


class BacktestEngine:
    def __init__(self, *, strategies: list[Strategy], config: BacktestConfig):
        self._strategies = strategies
        self._config = config
        self._risk_manager = RiskManager(config.risk_limits)

    def run(self, candles_by_timeframe: dict[Timeframe, list[Candle]]) -> BacktestResult:
        config = self._config
        dataframes = {
            tf.value: candles_to_dataframe(candles) for tf, candles in candles_by_timeframe.items()
        }
        primary_df = dataframes.get(config.primary_timeframe.value)

        if primary_df is None or primary_df.empty or len(primary_df) <= config.min_history_bars:
            return BacktestResult(
                trades=[],
                equity_curve=[],
                starting_balance=config.starting_balance,
                ending_balance=config.starting_balance,
            )

        balance = config.starting_balance
        peak_equity = balance
        trades: list[BacktestTrade] = []
        equity_curve: list[tuple[datetime, float]] = []
        open_positions: list[OpenPosition] = []
        rejected_signal_count = 0

        current_day: str | None = None
        current_week: str | None = None
        starting_balance_today = balance
        starting_balance_this_week = balance
        trades_today = 0

        for i in range(config.min_history_bars, len(primary_df)):
            current_time = primary_df.index[i]
            bar = primary_df.iloc[i]

            day_key = current_time.strftime("%Y-%m-%d")
            week_key = current_time.strftime("%G-W%V")  # ISO year/week
            if day_key != current_day:
                current_day = day_key
                starting_balance_today = balance
                trades_today = 0
            if week_key != current_week:
                current_week = week_key
                starting_balance_this_week = balance

            open_positions, balance = self._resolve_exits(
                open_positions, bar, current_time, config, trades, balance
            )

            peak_equity = max(peak_equity, balance)
            equity_curve.append((current_time, balance))

            sliced = {}
            for tf, df in dataframes.items():
                end_pos = df.index.searchsorted(current_time, side="right")
                start_pos = max(0, end_pos - config.context_lookback_bars)
                sliced[tf] = df.iloc[start_pos:end_pos]
            context = MarketContext(
                symbol=config.symbol, timeframes=sliced, spread_points=config.spread_points
            )
            signals = run_strategies(self._strategies, context)

            for signal in signals:
                account = AccountState(
                    balance=balance,
                    equity=balance,
                    starting_balance_today=starting_balance_today,
                    starting_balance_this_week=starting_balance_this_week,
                    peak_equity=peak_equity,
                    open_positions_count=len(open_positions),
                    trades_today=trades_today,
                )
                decision = self._risk_manager.evaluate(
                    signal=signal,
                    account=account,
                    current_spread_points=config.spread_points,
                    pip_value_per_lot=config.pip_value_per_lot,
                    pip_size=config.pip_size,
                    min_lot=config.min_lot,
                    max_lot=config.max_lot,
                )
                if not decision.approved:
                    rejected_signal_count += 1
                    continue

                open_positions.append(
                    OpenPosition(
                        position_id=str(uuid.uuid4()),
                        strategy_name=signal.strategy_name,
                        direction=signal.direction,
                        entry_time=current_time,
                        entry_price=signal.entry_price,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        volume=decision.volume,
                        risk_amount=decision.risk_amount,
                    )
                )
                trades_today += 1

        if open_positions:
            final_time = primary_df.index[-1]
            final_close = float(primary_df["close"].iloc[-1])
            for position in open_positions:
                pnl = _pnl(
                    position.direction, position.entry_price, final_close, position.volume, config
                )
                r_multiple = (pnl / position.risk_amount) if position.risk_amount else 0.0
                balance += pnl
                trades.append(
                    BacktestTrade(
                        strategy_name=position.strategy_name,
                        symbol=config.symbol,
                        direction=position.direction,
                        entry_time=position.entry_time,
                        entry_price=position.entry_price,
                        exit_time=final_time,
                        exit_price=final_close,
                        stop_loss=position.stop_loss,
                        take_profit=position.take_profit,
                        volume=position.volume,
                        pnl=pnl,
                        r_multiple=r_multiple,
                        exit_reason="end_of_data",
                    )
                )
            equity_curve.append((final_time, balance))

        return BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            starting_balance=config.starting_balance,
            ending_balance=balance,
            rejected_signal_count=rejected_signal_count,
        )

    @staticmethod
    def _resolve_exits(
        open_positions: list[OpenPosition],
        bar,
        current_time: datetime,
        config: BacktestConfig,
        trades: list[BacktestTrade],
        balance: float,
    ) -> tuple[list[OpenPosition], float]:
        still_open: list[OpenPosition] = []

        for position in open_positions:
            hit_sl = (
                bar["low"] <= position.stop_loss
                if position.direction == Direction.LONG
                else bar["high"] >= position.stop_loss
            )
            hit_tp = (
                bar["high"] >= position.take_profit
                if position.direction == Direction.LONG
                else bar["low"] <= position.take_profit
            )

            if hit_sl:
                exit_price, exit_reason = position.stop_loss, "stop_loss"
            elif hit_tp:
                exit_price, exit_reason = position.take_profit, "take_profit"
            else:
                still_open.append(position)
                continue

            pnl = _pnl(
                position.direction, position.entry_price, exit_price, position.volume, config
            )
            r_multiple = (pnl / position.risk_amount) if position.risk_amount else 0.0
            balance += pnl

            trades.append(
                BacktestTrade(
                    strategy_name=position.strategy_name,
                    symbol=config.symbol,
                    direction=position.direction,
                    entry_time=position.entry_time,
                    entry_price=position.entry_price,
                    exit_time=current_time,
                    exit_price=exit_price,
                    stop_loss=position.stop_loss,
                    take_profit=position.take_profit,
                    volume=position.volume,
                    pnl=pnl,
                    r_multiple=r_multiple,
                    exit_reason=exit_reason,
                )
            )

        return still_open, balance
