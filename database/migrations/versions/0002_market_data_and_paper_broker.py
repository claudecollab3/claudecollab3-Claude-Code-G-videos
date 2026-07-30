"""Add paper broker type and candles table for market data ingestion

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from database.types import GUID

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # PG12+ allows ADD VALUE inside a transaction as long as the new value
    # isn't used for writes in that same transaction (it isn't, here).
    op.execute("ALTER TYPE broker_type ADD VALUE IF NOT EXISTS 'paper'")

    op.create_table(
        "candles",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column(
            "timeframe",
            sa.Enum("M1", "M5", "M15", "M30", "H1", "H4", "D1", name="timeframe"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False, server_default="0"),
        sa.Column("spread_points", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_candles_symbol", "candles", ["symbol"])
    op.create_index("ix_candles_timeframe", "candles", ["timeframe"])
    op.create_index("ix_candles_timestamp", "candles", ["timestamp"])
    op.create_unique_constraint(
        "uq_candles_symbol_timeframe_timestamp", "candles", ["symbol", "timeframe", "timestamp"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_candles_symbol_timeframe_timestamp", "candles", type_="unique")
    op.drop_index("ix_candles_timestamp", table_name="candles")
    op.drop_index("ix_candles_timeframe", table_name="candles")
    op.drop_index("ix_candles_symbol", table_name="candles")
    op.drop_table("candles")

    bind = op.get_bind()
    sa.Enum(name="timeframe").drop(bind, checkfirst=True)
    # Postgres cannot remove a single value from an existing enum type, so
    # downgrading the 'paper' broker_type value itself is intentionally a
    # no-op here.
