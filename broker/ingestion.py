"""Market data ingestion: pulls OHLCV bars from a connected BrokerAdapter
across configured timeframes and persists them via MarketDataRepository.

This is the one piece of the pipeline that bridges `broker/` (live data) and
`database/` (the system of record) — strategies and the AI engine (Phase 4/5)
read from the database, never directly from a broker adapter, so historical
analysis and live analysis use identical data access code.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from broker.adapter import BrokerAdapter
from database.models.market_data import Timeframe
from database.repositories.market_data_repository import MarketDataRepository

DEFAULT_TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe.M1,
    Timeframe.M5,
    Timeframe.M15,
    Timeframe.M30,
    Timeframe.H1,
    Timeframe.H4,
    Timeframe.D1,
)


class MarketDataIngestionService:
    def __init__(self, *, adapter: BrokerAdapter, db: AsyncSession):
        self._adapter = adapter
        self._repository = MarketDataRepository(db)

    async def sync_symbol(
        self,
        symbol: str,
        *,
        timeframes: tuple[Timeframe, ...] = DEFAULT_TIMEFRAMES,
        count: int = 200,
    ) -> dict[str, int]:
        """Pull the latest `count` bars for each timeframe and upsert them.
        Returns {timeframe_value: bars_written}."""
        results: dict[str, int] = {}
        for timeframe in timeframes:
            candles = await self._adapter.get_ohlcv(symbol, timeframe, count=count)
            results[timeframe.value] = await self._repository.upsert_many(
                symbol, timeframe, candles
            )
        return results

    async def sync_symbols(self, symbols: list[str], **kwargs) -> dict[str, dict[str, int]]:
        return {symbol: await self.sync_symbol(symbol, **kwargs) for symbol in symbols}
