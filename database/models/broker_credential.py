"""Encrypted broker login storage.

Passwords/investor-passwords are never stored in plaintext: callers must
encrypt via `authentication.vault` before persisting and decrypt only
in-memory at the point of use (broker connection, Phase 3).
"""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPKMixin
from database.types import GUID

if TYPE_CHECKING:
    from database.models.user import User


class BrokerType(str, enum.Enum):
    MT5 = "mt5"
    MT4 = "mt4"


class BrokerCredential(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "broker_credentials"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=False, index=True
    )
    broker_type: Mapped[BrokerType] = mapped_column(
        Enum(BrokerType, name="broker_type"), nullable=False
    )
    broker_name: Mapped[str] = mapped_column(String(128), nullable=False)
    server: Mapped[str] = mapped_column(String(128), nullable=False)
    login: Mapped[str] = mapped_column(String(128), nullable=False)

    encrypted_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    encrypted_investor_password: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="broker_credentials")
