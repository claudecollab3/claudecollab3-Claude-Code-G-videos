"""Per-user trading & risk configuration.

Seeded from the process-wide defaults in `config/settings.py` but editable
per user/account so risk limits and strategy toggles are user-owned data,
not code constants. Enforcement of these values happens in `risk/`
(Phase 4); this module only defines the schema.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.settings import TradingMode
from database.base import Base, TimestampMixin, UUIDPKMixin
from database.types import GUID

if TYPE_CHECKING:
    from database.models.user import User


class TradingConfig(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "trading_configs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), unique=True, nullable=False, index=True
    )

    trading_mode: Mapped[TradingMode] = mapped_column(
        Enum(TradingMode, name="trading_mode"), default=TradingMode.PAPER, nullable=False
    )
    confidence_threshold: Mapped[float] = mapped_column(Float, default=90.0, nullable=False)

    risk_per_trade_percent: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_daily_loss_percent: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    max_weekly_loss_percent: Mapped[float] = mapped_column(Float, default=6.0, nullable=False)
    max_drawdown_percent: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    max_open_positions: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_trades_per_day: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_spread_points: Mapped[float] = mapped_column(Float, default=30.0, nullable=False)
    max_slippage_points: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    daily_profit_target_percent: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)

    news_trading_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    trade_news_blackout_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    enabled_strategies: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    notification_channels: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    account_size_profile: Mapped[str | None] = mapped_column(String(32), nullable=True)

    user: Mapped["User"] = relationship(back_populates="trading_config")
