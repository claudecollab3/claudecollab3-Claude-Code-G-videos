import pytest

from broker.adapter import BrokerConnectionError, OrderRequest, OrderSide
from broker.paper import PaperBrokerAdapter
from database.models.market_data import Timeframe


async def test_paper_adapter_requires_connect():
    adapter = PaperBrokerAdapter()
    with pytest.raises(BrokerConnectionError):
        await adapter.get_account_info()


async def test_paper_adapter_account_info():
    adapter = PaperBrokerAdapter(starting_balance=5000.0)
    await adapter.connect()
    info = await adapter.get_account_info()
    assert info.balance == 5000.0
    assert info.currency == "USD"


async def test_paper_adapter_ohlcv_length_and_order():
    adapter = PaperBrokerAdapter()
    await adapter.connect()
    candles = await adapter.get_ohlcv("EURUSD", Timeframe.M5, count=50)
    assert len(candles) == 50
    timestamps = [c.timestamp for c in candles]
    assert timestamps == sorted(timestamps)


async def test_paper_adapter_place_and_close_position():
    adapter = PaperBrokerAdapter()
    await adapter.connect()

    result = await adapter.place_order(
        OrderRequest(symbol="EURUSD", side=OrderSide.BUY, volume=1.0)
    )
    assert result.success
    assert result.broker_order_id is not None

    positions = await adapter.get_open_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "EURUSD"

    close_result = await adapter.close_position(result.broker_order_id)
    assert close_result.success
    assert await adapter.get_open_positions() == []


async def test_paper_adapter_modify_position():
    adapter = PaperBrokerAdapter()
    await adapter.connect()
    result = await adapter.place_order(
        OrderRequest(symbol="BTCUSD", side=OrderSide.SELL, volume=0.1)
    )
    modify_result = await adapter.modify_position(
        result.broker_order_id, stop_loss=1.5, take_profit=0.5
    )
    assert modify_result.success

    positions = await adapter.get_open_positions()
    assert positions[0].stop_loss == 1.5
    assert positions[0].take_profit == 0.5


async def test_paper_adapter_close_unknown_position_fails_gracefully():
    adapter = PaperBrokerAdapter()
    await adapter.connect()
    result = await adapter.close_position("does-not-exist")
    assert result.success is False
