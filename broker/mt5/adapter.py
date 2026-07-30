"""MetaTrader 5 adapter.

The official `MetaTrader5` Python package only works on Windows and requires
a running MT5 terminal on the same machine — real broker infrastructure,
not a design choice we can code around. The import is therefore deferred to
`connect()` so this module stays importable (for typing/tests/CI) on any
platform; attempting to actually connect anywhere else raises a clear
`BrokerConnectionError` instead of failing at import time.

The `MetaTrader5` package is itself synchronous (a blocking ctypes wrapper
around terminal IPC), so every call into it is offloaded via
`asyncio.to_thread` to avoid blocking the event loop.
"""

import asyncio
import time
from datetime import UTC, datetime
from typing import Any

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


class MT5BrokerAdapter(BrokerAdapter):
    def __init__(self, *, login: str, password: str, server: str):
        self._login = login
        self._password = password
        self._server = server
        self._mt5: Any = None
        self._timeframe_map: dict[Timeframe, int] = {}

    async def connect(self) -> None:
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise BrokerConnectionError(
                "The MetaTrader5 package is unavailable in this process. It only "
                "works on Windows with a running MT5 terminal installed; run this "
                "adapter on such a host (e.g. a dedicated Windows worker), not "
                "inside the main application process."
            ) from exc

        self._mt5 = mt5
        self._timeframe_map = {
            Timeframe.M1: mt5.TIMEFRAME_M1,
            Timeframe.M5: mt5.TIMEFRAME_M5,
            Timeframe.M15: mt5.TIMEFRAME_M15,
            Timeframe.M30: mt5.TIMEFRAME_M30,
            Timeframe.H1: mt5.TIMEFRAME_H1,
            Timeframe.H4: mt5.TIMEFRAME_H4,
            Timeframe.D1: mt5.TIMEFRAME_D1,
        }

        initialized = await asyncio.to_thread(
            mt5.initialize, login=int(self._login), password=self._password, server=self._server
        )
        if not initialized:
            code, description = mt5.last_error()
            self._mt5 = None
            raise BrokerConnectionError(f"MT5 initialize() failed: [{code}] {description}")

    async def disconnect(self) -> None:
        if self._mt5 is not None:
            await asyncio.to_thread(self._mt5.shutdown)
            self._mt5 = None

    async def is_connected(self) -> bool:
        if self._mt5 is None:
            return False
        info = await asyncio.to_thread(self._mt5.terminal_info)
        return info is not None

    def _require_connected(self) -> Any:
        if self._mt5 is None:
            raise BrokerConnectionError("MT5 adapter is not connected. Call connect() first.")
        return self._mt5

    async def get_account_info(self) -> AccountInfo:
        mt5 = self._require_connected()
        info = await asyncio.to_thread(mt5.account_info)
        if info is None:
            raise BrokerConnectionError(f"MT5 account_info() failed: {mt5.last_error()}")
        return AccountInfo(
            login=str(info.login),
            balance=info.balance,
            equity=info.equity,
            margin=info.margin,
            free_margin=info.margin_free,
            currency=info.currency,
            leverage=info.leverage,
            server=info.server,
        )

    async def get_quote(self, symbol: str) -> Quote:
        mt5 = self._require_connected()
        tick = await asyncio.to_thread(mt5.symbol_info_tick, symbol)
        if tick is None:
            raise BrokerConnectionError(f"No tick data for {symbol}: {mt5.last_error()}")
        return Quote(
            symbol=symbol,
            bid=tick.bid,
            ask=tick.ask,
            time=datetime.fromtimestamp(tick.time, tz=UTC),
        )

    async def get_ohlcv(
        self, symbol: str, timeframe: Timeframe, count: int = 200
    ) -> list[CandleData]:
        mt5 = self._require_connected()
        rates = await asyncio.to_thread(
            mt5.copy_rates_from_pos, symbol, self._timeframe_map[timeframe], 0, count
        )
        if rates is None:
            raise BrokerConnectionError(
                f"copy_rates_from_pos failed for {symbol}/{timeframe.value}: {mt5.last_error()}"
            )
        return [
            CandleData(
                timestamp=datetime.fromtimestamp(int(r["time"]), tz=UTC),
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
                volume=float(r["tick_volume"]),
                spread_points=float(r["spread"]),
            )
            for r in rates
        ]

    async def place_order(self, order: OrderRequest) -> OrderResult:
        mt5 = self._require_connected()
        quote = await self.get_quote(order.symbol)
        price = quote.ask if order.side == OrderSide.BUY else quote.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order.symbol,
            "volume": order.volume,
            "type": mt5.ORDER_TYPE_BUY if order.side == OrderSide.BUY else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": order.stop_loss or 0.0,
            "tp": order.take_profit or 0.0,
            "deviation": 10,
            "comment": order.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        start = time.perf_counter()
        result = await asyncio.to_thread(mt5.order_send, request)
        latency_ms = (time.perf_counter() - start) * 1000

        success = result is not None and result.retcode == mt5.TRADE_RETCODE_DONE
        return OrderResult(
            success=success,
            broker_order_id=str(result.order) if result else None,
            filled_price=result.price if result else None,
            filled_volume=result.volume if result else None,
            latency_ms=latency_ms,
            message=result.comment if result else "order_send returned None",
        )

    async def close_position(self, position_id: str, *, volume: float | None = None) -> OrderResult:
        mt5 = self._require_connected()
        positions = await asyncio.to_thread(mt5.positions_get, ticket=int(position_id))
        if not positions:
            return OrderResult(
                success=False,
                broker_order_id=None,
                filled_price=None,
                filled_volume=None,
                latency_ms=0.0,
                message="position not found",
            )

        position = positions[0]
        close_volume = volume if volume is not None else position.volume
        side = OrderSide.SELL if position.type == mt5.POSITION_TYPE_BUY else OrderSide.BUY
        quote = await self.get_quote(position.symbol)
        price = quote.bid if side == OrderSide.SELL else quote.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": close_volume,
            "type": mt5.ORDER_TYPE_SELL if side == OrderSide.SELL else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": price,
            "deviation": 10,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = await asyncio.to_thread(mt5.order_send, request)
        success = result is not None and result.retcode == mt5.TRADE_RETCODE_DONE
        return OrderResult(
            success=success,
            broker_order_id=str(position.ticket),
            filled_price=result.price if result else None,
            filled_volume=result.volume if result else None,
            latency_ms=0.0,
            message=result.comment if result else "close failed",
        )

    async def modify_position(
        self,
        position_id: str,
        *,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderResult:
        mt5 = self._require_connected()
        positions = await asyncio.to_thread(mt5.positions_get, ticket=int(position_id))
        if not positions:
            return OrderResult(
                success=False,
                broker_order_id=None,
                filled_price=None,
                filled_volume=None,
                latency_ms=0.0,
                message="position not found",
            )

        position = positions[0]
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": position.ticket,
            "sl": stop_loss if stop_loss is not None else position.sl,
            "tp": take_profit if take_profit is not None else position.tp,
        }
        result = await asyncio.to_thread(mt5.order_send, request)
        success = result is not None and result.retcode == mt5.TRADE_RETCODE_DONE
        return OrderResult(
            success=success,
            broker_order_id=str(position.ticket),
            filled_price=None,
            filled_volume=None,
            latency_ms=0.0,
            message=result.comment if result else "modify failed",
        )

    async def get_open_positions(self) -> list[Position]:
        mt5 = self._require_connected()
        positions = await asyncio.to_thread(mt5.positions_get) or ()
        return [
            Position(
                position_id=str(p.ticket),
                symbol=p.symbol,
                side=OrderSide.BUY if p.type == mt5.POSITION_TYPE_BUY else OrderSide.SELL,
                volume=p.volume,
                open_price=p.price_open,
                current_price=p.price_current,
                stop_loss=p.sl or None,
                take_profit=p.tp or None,
                profit=p.profit,
                opened_at=datetime.fromtimestamp(p.time, tz=UTC),
            )
            for p in positions
        ]
