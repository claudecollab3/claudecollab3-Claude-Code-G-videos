"""Query layer for persisted OHLCV bars."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from broker.adapter import CandleData
from database.models.market_data import Candle, Timeframe


class MarketDataRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest(
        self, symbol: str, timeframe: Timeframe, *, limit: int = 200
    ) -> list[Candle]:
        result = await self.db.execute(
            select(Candle)
            .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
            .order_by(Candle.timestamp.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def get_one(
        self, symbol: str, timeframe: Timeframe, timestamp: datetime
    ) -> Candle | None:
        result = await self.db.execute(
            select(Candle).where(
                Candle.symbol == symbol,
                Candle.timeframe == timeframe,
                Candle.timestamp == timestamp,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_candle(self, symbol: str, timeframe: Timeframe, candle: CandleData) -> Candle:
        existing = await self.get_one(symbol, timeframe, candle.timestamp)
        if existing is None:
            existing = Candle(symbol=symbol, timeframe=timeframe, timestamp=candle.timestamp)
            self.db.add(existing)

        existing.open = candle.open
        existing.high = candle.high
        existing.low = candle.low
        existing.close = candle.close
        existing.volume = candle.volume
        existing.spread_points = candle.spread_points
        await self.db.flush()
        return existing

    async def upsert_many(
        self, symbol: str, timeframe: Timeframe, candles: list[CandleData]
    ) -> int:
        for candle in candles:
            await self.upsert_candle(symbol, timeframe, candle)
        return len(candles)
