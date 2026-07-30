"""AI ensemble prediction endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.features import build_feature_vector
from ai.registry import build_default_ensemble
from authentication.dependencies import get_current_user
from backend.app.schemas.ai import ModelVoteResponse, PredictRequest, PredictResponse
from database.models.user import User
from database.repositories.ai_prediction_repository import AIPredictionRepository
from database.repositories.market_data_repository import MarketDataRepository
from database.session import get_db
from strategies.base import MarketContext
from strategies.data import candles_to_dataframe

router = APIRouter(prefix="/ai", tags=["ai"])

_ensemble = build_default_ensemble()


@router.post("/predict", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PredictResponse:
    market_data = MarketDataRepository(db)
    timeframes = {}
    for timeframe in payload.timeframes:
        candles = await market_data.get_latest(
            payload.symbol.upper(), timeframe, limit=payload.candle_limit
        )
        timeframes[timeframe.value] = candles_to_dataframe(candles)

    context = MarketContext(symbol=payload.symbol.upper(), timeframes=timeframes, spread_points=0.0)
    features = build_feature_vector(context)
    result = _ensemble.predict(features)

    model_votes = [
        {
            "model_name": v.model_name,
            "direction": v.direction.value,
            "probability": v.probability,
            "confidence": v.confidence,
            "fitted": v.fitted,
        }
        for v in result.votes
    ]

    await AIPredictionRepository(db).create(
        symbol=context.symbol,
        direction=result.direction.value,
        confidence=result.confidence,
        model_votes=model_votes,
        weights=result.weights,
        features=features,
    )

    return PredictResponse(
        symbol=context.symbol,
        direction=result.direction.value,
        confidence=result.confidence,
        votes=[
            ModelVoteResponse(
                model_name=v.model_name,
                direction=v.direction.value,
                probability=v.probability,
                confidence=v.confidence,
                fitted=v.fitted,
            )
            for v in result.votes
        ],
        weights=result.weights,
    )
