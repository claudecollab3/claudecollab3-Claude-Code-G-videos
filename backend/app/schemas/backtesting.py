from pydantic import BaseModel, Field

from database.models.market_data import Timeframe


class BacktestRequest(BaseModel):
    symbol: str = Field(max_length=32)
    primary_timeframe: Timeframe = Timeframe.H1
    auxiliary_timeframes: list[Timeframe] = Field(
        default_factory=lambda: [Timeframe.M15, Timeframe.H4]
    )
    candle_limit: int = Field(default=2000, ge=100, le=20000)
    starting_balance: float = Field(default=10_000.0, gt=0)
    spread_points: float = 10.0
    min_history_bars: int = Field(default=60, ge=10)


class PerformanceReportResponse(BaseModel):
    total_trades: int
    win_rate: float
    profit_factor: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown_percent: float
    average_win: float
    average_loss: float
    expectancy: float
    monthly_returns: dict[str, float]
    yearly_returns: dict[str, float]


class EquityCurvePointResponse(BaseModel):
    timestamp: str
    equity: float


class BacktestTradeResponse(BaseModel):
    strategy_name: str
    symbol: str
    direction: str
    entry_time: str
    entry_price: float
    exit_time: str
    exit_price: float
    stop_loss: float
    take_profit: float
    volume: float
    pnl: float
    r_multiple: float
    exit_reason: str


class BacktestResponse(BaseModel):
    symbol: str
    starting_balance: float
    ending_balance: float
    rejected_signal_count: int
    performance: PerformanceReportResponse
    equity_curve: list[EquityCurvePointResponse]
    trades: list[BacktestTradeResponse]
