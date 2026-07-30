"""Query layer for persisted AI ensemble predictions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ai_prediction import AIPrediction


class AIPredictionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        symbol: str,
        direction: str,
        confidence: float,
        model_votes: list[dict],
        weights: dict[str, float],
        features: dict[str, float],
    ) -> AIPrediction:
        prediction = AIPrediction(
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            model_votes=model_votes,
            weights=weights,
            features=features,
        )
        self.db.add(prediction)
        await self.db.flush()
        await self.db.refresh(prediction)
        return prediction

    async def list_recent(self, symbol: str, *, limit: int = 50) -> list[AIPrediction]:
        result = await self.db.execute(
            select(AIPrediction)
            .where(AIPrediction.symbol == symbol)
            .order_by(AIPrediction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
