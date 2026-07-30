"""Executes a risk-approved Signal against a connected BrokerAdapter with
retry-on-transient-error and latency logging. Broker-agnostic: depends only
on the BrokerAdapter interface, so the same engine runs unchanged against
MT5, MT4, or paper trading."""

import time

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from broker.adapter import (
    BrokerAdapter,
    BrokerConnectionError,
    OrderRequest,
    OrderResult,
    OrderSide,
)
from risk.manager import RiskDecision
from strategies.base import Direction, Signal


class ExecutionEngine:
    def __init__(self, adapter: BrokerAdapter):
        self._adapter = adapter

    @retry(
        retry=retry_if_exception_type(BrokerConnectionError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def execute(self, signal: Signal, decision: RiskDecision) -> OrderResult:
        if not decision.approved:
            raise ValueError("Cannot execute a signal the risk manager rejected")

        order = OrderRequest(
            symbol=signal.symbol,
            side=OrderSide.BUY if signal.direction == Direction.LONG else OrderSide.SELL,
            volume=decision.volume,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            comment=f"{signal.strategy_name}|conf={signal.confidence:.0f}",
        )

        start = time.perf_counter()
        result = await self._adapter.place_order(order)
        if not result.latency_ms:
            result.latency_ms = (time.perf_counter() - start) * 1000
        return result
