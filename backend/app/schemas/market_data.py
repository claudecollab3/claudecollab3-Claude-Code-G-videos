from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from database.models.market_data import Timeframe


class CandleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    spread_points: float | None


class SyncMarketDataRequest(BaseModel):
    broker_credential_id: str
    symbol: str = Field(max_length=32)
    timeframes: list[Timeframe] | None = None
    count: int = Field(default=200, ge=1, le=5000)
