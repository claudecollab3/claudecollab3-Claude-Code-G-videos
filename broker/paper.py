"""Paper-trading adapter: simulates fills and positions against a supplied
quote source, without touching a real broker.

Used for demo/paper trading, Phase 6 backtesting fills, and as the target
for `BrokerType.PAPER` credentials so the whole broker/execution code path
is exercisable in development and CI without a live MT4/MT5 terminal.
"""

import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from broker.adapter import (
    AccountInfo,
    BrokerAdapter,
    BrokerConnectionError,
    CandleData,
    OrderRequest,
    OrderResult,
    OrderSide,
    Position,
    Quote,
)
from database.models.market_data import Timeframe

_TIMEFRAME_SECONDS: dict[Timeframe, int] = {
    Timeframe.M1: 60,
    Timeframe.M5: 300,
    Timeframe.M15: 900,
    Timeframe.M30: 1800,
    Timeframe.H1: 3600,
    Timeframe.H4: 14400,
    Timeframe.D1: 86400,
}


class PaperBrokerAdapter(BrokerAdapter):
    def __init__(
        self,
        *,
        starting_balance: float = 10_000.0,
        quote_provider: Callable[[str], Quote] | None = None,
    ):
        self._connected = False
        self._balance = starting_balance
        self._equity = starting_balance
        self._positions: dict[str, Position] = {}
        self._quote_provider = quote_provider or self._synthetic_quote

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def is_connected(self) -> bool:
        return self._connected

    def _require_connected(self) -> None:
        if not self._connected:
            raise BrokerConnectionError("Paper broker is not connected")

    @staticmethod
    def _synthetic_quote(symbol: str) -> Quote:
        # Deterministic pseudo-price (stable per symbol, no external state)
        # so tests and demos are reproducible.
        base = 1.0 + (abs(hash(symbol)) % 10000) / 10000
        return Quote(symbol=symbol, bid=base, ask=base + 0.0002, time=datetime.now(UTC))

    async def get_account_info(self) -> AccountInfo:
        self._require_connected()
        return AccountInfo(
            login="paper",
            balance=self._balance,
            equity=self._equity,
            margin=0.0,
            free_margin=self._equity,
            currency="USD",
            leverage=100,
            server="paper-trading",
        )

    async def get_quote(self, symbol: str) -> Quote:
        self._require_connected()
        return self._quote_provider(symbol)

    async def get_ohlcv(
        self, symbol: str, timeframe: Timeframe, count: int = 200
    ) -> list[CandleData]:
        self._require_connected()
        step = _TIMEFRAME_SECONDS[timeframe]
        quote = await self.get_quote(symbol)
        anchor = quote.time.replace(second=0, microsecond=0)
        price = quote.bid

        candles = []
        for i in range(count, 0, -1):
            ts = anchor - timedelta(seconds=step * i)
            candles.append(
                CandleData(
                    timestamp=ts,
                    open=price,
                    high=price * 1.0005,
                    low=price * 0.9995,
                    close=price,
                    volume=1.0,
                )
            )
        return candles

    async def place_order(self, order: OrderRequest) -> OrderResult:
        self._require_connected()
        start = time.perf_counter()
        quote = await self.get_quote(order.symbol)
        fill_price = quote.ask if order.side == OrderSide.BUY else quote.bid

        position_id = str(uuid.uuid4())
        self._positions[position_id] = Position(
            position_id=position_id,
            symbol=order.symbol,
            side=order.side,
            volume=order.volume,
            open_price=fill_price,
            current_price=fill_price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            profit=0.0,
            opened_at=datetime.now(UTC),
        )

        return OrderResult(
            success=True,
            broker_order_id=position_id,
            filled_price=fill_price,
            filled_volume=order.volume,
            latency_ms=(time.perf_counter() - start) * 1000,
            message="filled",
        )

    async def close_position(self, position_id: str, *, volume: float | None = None) -> OrderResult:
        self._require_connected()
        position = self._positions.get(position_id)
        if position is None:
            return OrderResult(
                success=False,
                broker_order_id=None,
                filled_price=None,
                filled_volume=None,
                latency_ms=0.0,
                message="position not found",
            )

        quote = await self.get_quote(position.symbol)
        close_price = quote.bid if position.side == OrderSide.BUY else quote.ask
        closed_volume = volume if volume is not None else position.volume
        direction = 1 if position.side == OrderSide.BUY else -1
        pnl = direction * (close_price - position.open_price) * closed_volume
        self._balance += pnl
        self._equity = self._balance

        if volume is not None and volume < position.volume:
            position.volume -= volume
        else:
            del self._positions[position_id]

        return OrderResult(
            success=True,
            broker_order_id=position_id,
            filled_price=close_price,
            filled_volume=closed_volume,
            latency_ms=0.0,
            message="closed",
        )

    async def modify_position(
        self,
        position_id: str,
        *,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderResult:
        self._require_connected()
        position = self._positions.get(position_id)
        if position is None:
            return OrderResult(
                success=False,
                broker_order_id=None,
                filled_price=None,
                filled_volume=None,
                latency_ms=0.0,
                message="position not found",
            )

        if stop_loss is not None:
            position.stop_loss = stop_loss
        if take_profit is not None:
            position.take_profit = take_profit

        return OrderResult(
            success=True,
            broker_order_id=position_id,
            filled_price=position.current_price,
            filled_volume=position.volume,
            latency_ms=0.0,
            message="modified",
        )

    async def get_open_positions(self) -> list[Position]:
        self._require_connected()
        return list(self._positions.values())
