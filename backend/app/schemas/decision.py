from pydantic import BaseModel, Field

from backend.app.schemas.signals import AccountStateRequest, RiskDecisionResponse
from database.models.market_data import Timeframe


class EvaluateDecisionRequest(BaseModel):
    symbol: str = Field(max_length=32)
    timeframes: list[Timeframe] = Field(
        default_factory=lambda: [Timeframe.M15, Timeframe.H1, Timeframe.H4]
    )
    candle_limit: int = Field(default=300, ge=50, le=5000)
    current_spread_points: float = 10.0
    account: AccountStateRequest


class ChecklistItemResponse(BaseModel):
    name: str
    passed: bool
    detail: str


class ConfirmedSignalResponse(BaseModel):
    strategy_name: str
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    reasons: list[str]
    checklist: list[ChecklistItemResponse]
    risk_decision: RiskDecisionResponse
