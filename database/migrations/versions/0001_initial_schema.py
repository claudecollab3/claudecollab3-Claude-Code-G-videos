"""Initial schema: users, sessions, audit trail, broker credentials, trading config

Revision ID: 0001
Revises:
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from database.types import GUID

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("admin", "trader", "viewer", name="user_role"),
            nullable=False,
            server_default="trader",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("totp_secret", sa.String(64), nullable=True),
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_sessions",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("resource", sa.String(128), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    op.create_table(
        "broker_credentials",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("broker_type", sa.Enum("mt5", "mt4", name="broker_type"), nullable=False),
        sa.Column("broker_name", sa.String(128), nullable=False),
        sa.Column("server", sa.String(128), nullable=False),
        sa.Column("login", sa.String(128), nullable=False),
        sa.Column("encrypted_password", sa.String(1024), nullable=False),
        sa.Column("encrypted_investor_password", sa.String(1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_broker_credentials_user_id", "broker_credentials", ["user_id"])

    op.create_table(
        "trading_configs",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column(
            "trading_mode",
            sa.Enum("manual", "semi_auto", "full_auto", "paper", "backtest", name="trading_mode"),
            nullable=False,
            server_default="paper",
        ),
        sa.Column("confidence_threshold", sa.Float(), nullable=False, server_default="90.0"),
        sa.Column("risk_per_trade_percent", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("max_daily_loss_percent", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("max_weekly_loss_percent", sa.Float(), nullable=False, server_default="6.0"),
        sa.Column("max_drawdown_percent", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("max_open_positions", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("max_trades_per_day", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_spread_points", sa.Float(), nullable=False, server_default="30.0"),
        sa.Column("max_slippage_points", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("daily_profit_target_percent", sa.Float(), nullable=False, server_default="2.0"),
        sa.Column("news_trading_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("trade_news_blackout_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("enabled_strategies", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("notification_channels", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("account_size_profile", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trading_configs_user_id", "trading_configs", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("trading_configs")
    op.drop_table("broker_credentials")
    op.drop_table("audit_logs")
    op.drop_table("user_sessions")
    op.drop_table("users")

    bind = op.get_bind()
    sa.Enum(name="trading_mode").drop(bind, checkfirst=True)
    sa.Enum(name="broker_type").drop(bind, checkfirst=True)
    sa.Enum(name="user_role").drop(bind, checkfirst=True)
