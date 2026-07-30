"""Persisted OHLCV bars.

`Timeframe` is the canonical enum for the multi-timeframe analysis the spec
calls for (M1..D1); it's defined here (alongside the column that uses it,
following the pattern of `Role`/`BrokerType`/`TradingMode`) and imported by
`broker/` and `strategies/` rather than redefined per module.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDPKMixin


class Timeframe(str, enum.Enum):
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


class Candle(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "timeframe", "timestamp", name="uq_candles_symbol_timeframe_timestamp"
        ),
    )

    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    timeframe: Mapped[Timeframe] = mapped_column(
        Enum(Timeframe, name="timeframe"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    spread_points: Mapped[float | None] = mapped_column(Float, nullable=True)
