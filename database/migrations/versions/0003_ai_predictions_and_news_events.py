"""Add ai_predictions and news_events tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from database.types import GUID

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_predictions",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_votes", sa.JSON(), nullable=False),
        sa.Column("weights", sa.JSON(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ai_predictions_symbol", "ai_predictions", ["symbol"])

    op.create_table(
        "news_events",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("external_id", sa.String(128), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("currency", sa.String(16), nullable=False),
        sa.Column("impact", sa.Enum("low", "medium", "high", name="news_impact"), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("forecast", sa.String(64), nullable=True),
        sa.Column("previous", sa.String(64), nullable=True),
        sa.Column("actual", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_news_events_external_id", "news_events", ["external_id"], unique=True)
    op.create_index("ix_news_events_currency", "news_events", ["currency"])
    op.create_index("ix_news_events_event_time", "news_events", ["event_time"])


def downgrade() -> None:
    op.drop_table("news_events")
    op.drop_table("ai_predictions")

    bind = op.get_bind()
    sa.Enum(name="news_impact").drop(bind, checkfirst=True)
