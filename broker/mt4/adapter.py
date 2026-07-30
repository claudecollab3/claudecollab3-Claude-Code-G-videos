"""MetaTrader 4 adapter.

MT4 has no official Python API, so this bridges to an Expert Advisor running
inside the MT4 terminal via a lightweight ZeroMQ request/response protocol
(the common "DWX-style" pattern: a PUSH socket for commands, a PULL socket
for responses). This module defines the transport and message contract; it
requires a compatible EA deployed in the MT4 terminal on the other end to
actually respond — there is nothing to connect to in this sandbox/CI.
"""

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

import zmq
import zmq.asyncio

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

_TIMEFRAME_CODES: dict[Timeframe, int] = {
    Timeframe.M1: 1,
    Timeframe.M5: 5,
    Timeframe.M15: 15,
    Timeframe.M30: 30,
    Timeframe.H1: 60,
    Timeframe.H4: 240,
    Timeframe.D1: 1440,
}


class MT4BrokerAdapter(BrokerAdapter):
    """Talks to a DWX-style ZeroMQ bridge EA. `host`/`push_port` (commands)
    and `pull_port` (responses) must match the EA's configuration."""

    def __init__(self, *, host: str, push_port: int, pull_port: int, request_timeout: float = 5.0):
        self._host = host
        self._push_port = push_port
        self._pull_port = pull_port
        self._timeout = request_timeout
        self._context: zmq.asyncio.Context | None = None
        self._push_socket: Any = None
        self._pull_socket: Any = None

    async def connect(self) -> None:
        self._context = zmq.asyncio.Context()
        self._push_socket = self._context.socket(zmq.PUSH)
        self._push_socket.connect(f"tcp://{self._host}:{self._push_port}")
        self._pull_socket = self._context.socket(zmq.PULL)
        self._pull_socket.connect(f"tcp://{self._host}:{self._pull_port}")

        try:
            await self._request({"action": "PING"})
        except BrokerConnectionError:
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        if self._push_socket is not None:
            self._push_socket.close(linger=0)
        if self._pull_socket is not None:
            self._pull_socket.close(linger=0)
        if self._context is not None:
            self._context.term()
        self._push_socket = None
        self._pull_socket = None
        self._context = None

    async def is_connected(self) -> bool:
        return self._push_socket is not None and self._pull_socket is not None

    def _require_connected(self) -> None:
        if self._push_socket is None or self._pull_socket is None:
            raise BrokerConnectionError("MT4 bridge is not connected. Call connect() first.")

    async def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        message = {**payload, "_id": str(uuid.uuid4())}
        await self._push_socket.send_json(message)
        try:
            raw = await asyncio.wait_for(self._pull_socket.recv_json(), timeout=self._timeout)
        except TimeoutError as exc:
            raise BrokerConnectionError(
                f"MT4 bridge did not respond within {self._timeout}s. Is the EA "
                "running and listening on the configured host/ports?"
            ) from exc

        if raw.get("error"):
            raise BrokerConnectionError(f"MT4 bridge error: {raw['error']}")
        return raw

    async def get_account_info(self) -> AccountInfo:
        r = await self._request({"action": "ACCOUNT_INFO"})
        return AccountInfo(
            login=str(r["login"]),
            balance=r["balance"],
            equity=r["equity"],
            margin=r["margin"],
            free_margin=r["free_margin"],
            currency=r["currency"],
            leverage=r["leverage"],
            server=r["server"],
        )

    async def get_quote(self, symbol: str) -> Quote:
        r = await self._request({"action": "QUOTE", "symbol": symbol})
        return Quote(
            symbol=symbol,
            bid=r["bid"],
            ask=r["ask"],
            time=datetime.fromtimestamp(r["time"], tz=UTC),
        )

    async def get_ohlcv(
        self, symbol: str, timeframe: Timeframe, count: int = 200
    ) -> list[CandleData]:
        r = await self._request(
            {
                "action": "OHLCV",
                "symbol": symbol,
                "timeframe": _TIMEFRAME_CODES[timeframe],
                "count": count,
            }
        )
        return [
            CandleData(
                timestamp=datetime.fromtimestamp(bar["time"], tz=UTC),
                open=bar["open"],
                high=bar["high"],
                low=bar["low"],
                close=bar["close"],
                volume=bar.get("volume", 0.0),
            )
            for bar in r["bars"]
        ]

    async def place_order(self, order: OrderRequest) -> OrderResult:
        r = await self._request(
            {
                "action": "ORDER_SEND",
                "symbol": order.symbol,
                "side": order.side.value,
                "volume": order.volume,
                "sl": order.stop_loss,
                "tp": order.take_profit,
                "comment": order.comment,
            }
        )
        return OrderResult(
            success=r.get("success", False),
            broker_order_id=str(r["ticket"]) if r.get("ticket") else None,
            filled_price=r.get("price"),
            filled_volume=r.get("volume"),
            latency_ms=r.get("latency_ms", 0.0),
            message=r.get("message", ""),
        )

    async def close_position(self, position_id: str, *, volume: float | None = None) -> OrderResult:
        r = await self._request(
            {"action": "ORDER_CLOSE", "ticket": int(position_id), "volume": volume}
        )
        return OrderResult(
            success=r.get("success", False),
            broker_order_id=position_id,
            filled_price=r.get("price"),
            filled_volume=r.get("volume"),
            latency_ms=r.get("latency_ms", 0.0),
            message=r.get("message", ""),
        )

    async def modify_position(
        self,
        position_id: str,
        *,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderResult:
        r = await self._request(
            {
                "action": "ORDER_MODIFY",
                "ticket": int(position_id),
                "sl": stop_loss,
                "tp": take_profit,
            }
        )
        return OrderResult(
            success=r.get("success", False),
            broker_order_id=position_id,
            filled_price=None,
            filled_volume=None,
            latency_ms=r.get("latency_ms", 0.0),
            message=r.get("message", ""),
        )

    async def get_open_positions(self) -> list[Position]:
        r = await self._request({"action": "POSITIONS"})
        return [
            Position(
                position_id=str(p["ticket"]),
                symbol=p["symbol"],
                side=OrderSide(p["side"]),
                volume=p["volume"],
                open_price=p["open_price"],
                current_price=p["current_price"],
                stop_loss=p.get("sl"),
                take_profit=p.get("tp"),
                profit=p["profit"],
                opened_at=datetime.fromtimestamp(p["time"], tz=UTC),
            )
            for p in r.get("positions", [])
        ]
