from datetime import UTC, datetime

from broker.adapter import Quote
from broker.ingestion import MarketDataIngestionService
from broker.paper import PaperBrokerAdapter
from database.models.market_data import Timeframe
from database.repositories.market_data_repository import MarketDataRepository

_FIXED_QUOTE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _fixed_quote_provider(symbol: str) -> Quote:
    return Quote(symbol=symbol, bid=1.1, ask=1.1002, time=_FIXED_QUOTE_TIME)


async def test_sync_symbol_persists_candles(db_session):
    adapter = PaperBrokerAdapter(quote_provider=_fixed_quote_provider)
    await adapter.connect()

    service = MarketDataIngestionService(adapter=adapter, db=db_session)
    results = await service.sync_symbol("EURUSD", timeframes=(Timeframe.M1, Timeframe.M5), count=30)
    await db_session.commit()

    assert results == {"M1": 30, "M5": 30}

    candles = await MarketDataRepository(db_session).get_latest("EURUSD", Timeframe.M1, limit=100)
    assert len(candles) == 30


async def test_sync_symbol_upserts_without_duplicating(db_session):
    adapter = PaperBrokerAdapter(quote_provider=_fixed_quote_provider)
    await adapter.connect()
    service = MarketDataIngestionService(adapter=adapter, db=db_session)

    await service.sync_symbol("BTCUSD", timeframes=(Timeframe.M1,), count=20)
    await service.sync_symbol("BTCUSD", timeframes=(Timeframe.M1,), count=20)
    await db_session.commit()

    candles = await MarketDataRepository(db_session).get_latest("BTCUSD", Timeframe.M1, limit=100)
    assert len(candles) == 20
