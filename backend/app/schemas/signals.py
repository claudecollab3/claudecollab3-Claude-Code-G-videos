from pydantic import BaseModel, Field

from database.models.market_data import Timeframe


class AccountStateRequest(BaseModel):
    balance: float
    equity: float
    starting_balance_today: float
    starting_balance_this_week: float
    peak_equity: float
    open_positions_count: int = 0
    trades_today: int = 0
    emergency_stop: bool = False


class EvaluateSignalsRequest(BaseModel):
    symbol: str = Field(max_length=32)
    timeframes: list[Timeframe] = Field(
        default_factory=lambda: [Timeframe.M15, Timeframe.H1, Timeframe.H4]
    )
    candle_limit: int = Field(default=200, ge=50, le=2000)
    current_spread_points: float = 10.0
    account: AccountStateRequest


class RiskDecisionResponse(BaseModel):
    approved: bool
    reason: str
    volume: float
    risk_amount: float


class SignalResponse(BaseModel):
    strategy_name: str
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    reasons: list[str]
    risk_decision: RiskDecisionResponse
