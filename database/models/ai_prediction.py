"""Stores every AI ensemble prediction for audit/history and future
retraining/backtesting analysis (Phase 6)."""

from sqlalchemy import JSON, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDPKMixin


class AIPrediction(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "ai_predictions"

    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_votes: Mapped[list] = mapped_column(JSON, nullable=False)
    weights: Mapped[dict] = mapped_column(JSON, nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
