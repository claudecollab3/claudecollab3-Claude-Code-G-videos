from pydantic import BaseModel, ConfigDict, Field

from database.models.market_data import Timeframe


class ModelVoteResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    direction: str
    probability: float
    confidence: float
    fitted: bool


class PredictRequest(BaseModel):
    symbol: str = Field(max_length=32)
    timeframes: list[Timeframe] = Field(
        default_factory=lambda: [Timeframe.M15, Timeframe.H1, Timeframe.H4]
    )
    candle_limit: int = Field(default=300, ge=50, le=5000)


class PredictResponse(BaseModel):
    symbol: str
    direction: str
    confidence: float
    votes: list[ModelVoteResponse]
    weights: dict[str, float]
