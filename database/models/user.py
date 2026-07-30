"""User account model."""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPKMixin

if TYPE_CHECKING:
    from database.models.broker_credential import BrokerCredential
    from database.models.trading_config import TradingConfig
    from database.models.user_session import UserSession


class Role(str, enum.Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"


class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role"), default=Role.TRADER, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    broker_credentials: Mapped[list["BrokerCredential"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    trading_config: Mapped["TradingConfig | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} role={self.role}>"
