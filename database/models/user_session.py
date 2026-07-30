"""Refresh-token sessions, one row per issued refresh token.

Storing a hash of the refresh token (never the token itself) lets us revoke
individual sessions ("log out this device") and detect reuse of a revoked
token, without being able to reconstruct the token from the database.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPKMixin
from database.types import GUID

if TYPE_CHECKING:
    from database.models.user import User


class UserSession(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None
