import pytest

from broker.paper import PaperBrokerAdapter
from execution.engine import ExecutionEngine
from risk.manager import RiskDecision
from strategies.base import Direction, Signal


async def test_execution_engine_places_order_on_approved_decision():
    adapter = PaperBrokerAdapter()
    await adapter.connect()
    engine = ExecutionEngine(adapter)

    signal = Signal(
        strategy_name="trend_following",
        symbol="EURUSD",
        direction=Direction.LONG,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        confidence=95.0,
    )
    decision = RiskDecision(approved=True, reason="approved", volume=0.5, risk_amount=10.0)

    result = await engine.execute(signal, decision)
    assert result.success
    assert result.filled_volume == 0.5

    positions = await adapter.get_open_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "EURUSD"


async def test_execution_engine_refuses_rejected_decision():
    adapter = PaperBrokerAdapter()
    await adapter.connect()
    engine = ExecutionEngine(adapter)

    signal = Signal(
        strategy_name="trend_following",
        symbol="EURUSD",
        direction=Direction.LONG,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        confidence=50.0,
    )
    decision = RiskDecision(approved=False, reason="Confidence too low")

    with pytest.raises(ValueError):
        await engine.execute(signal, decision)
