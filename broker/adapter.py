"""Common interface every broker integration (MT5, MT4, paper) implements.

Strategies, risk management, and execution all depend only on this
interface, never on a concrete adapter, so the same code runs unchanged
against a live MT5 account, an MT4 bridge, or a paper-trading simulation.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from database.models.market_data import Timeframe

__all__ = [
    "OrderSide",
    "OrderType",
    "AccountInfo",
    "SymbolInfo",
    "Quote",
    "CandleData",
    "OrderRequest",
    "OrderResult",
    "Position",
    "BrokerConnectionError",
    "BrokerAdapter",
]


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


@dataclass
class AccountInfo:
    login: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    currency: str
    leverage: int
    server: str


@dataclass
class SymbolInfo:
    symbol: str
    digits: int
    point: float
    min_lot: float
    max_lot: float
    lot_step: float
    contract_size: float


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    time: datetime

    @property
    def spread_points(self) -> float:
        return self.ask - self.bid


@dataclass
class CandleData:
    """A single OHLCV bar as returned by a broker adapter (not yet persisted)."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    spread_points: float | None = None


@dataclass
class OrderRequest:
    symbol: str
    side: OrderSide
    volume: float
    order_type: OrderType = OrderType.MARKET
    price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    comment: str = ""
    client_order_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class OrderResult:
    success: bool
    broker_order_id: str | None
    filled_price: float | None
    filled_volume: float | None
    latency_ms: float
    message: str = ""


@dataclass
class Position:
    position_id: str
    symbol: str
    side: OrderSide
    volume: float
    open_price: float
    current_price: float
    stop_loss: float | None
    take_profit: float | None
    profit: float
    opened_at: datetime


class BrokerConnectionError(RuntimeError):
    """Raised when a broker adapter cannot establish or maintain a connection."""


class BrokerAdapter(ABC):
    """Every broker integration (MT5, MT4, paper) implements this."""

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def is_connected(self) -> bool: ...

    @abstractmethod
    async def get_account_info(self) -> AccountInfo: ...

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote: ...

    @abstractmethod
    async def get_ohlcv(
        self, symbol: str, timeframe: Timeframe, count: int = 200
    ) -> list[CandleData]: ...

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResult: ...

    @abstractmethod
    async def close_position(
        self, position_id: str, *, volume: float | None = None
    ) -> OrderResult: ...

    @abstractmethod
    async def modify_position(
        self,
        position_id: str,
        *,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderResult: ...

    @abstractmethod
    async def get_open_positions(self) -> list[Position]: ...
