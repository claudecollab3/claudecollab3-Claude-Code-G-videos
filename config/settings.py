"""Centralized, environment-driven application configuration.

All runtime configuration flows through this module so no module reaches
into `os.environ` directly. Values are loaded from the process environment
(and a local `.env` file in development) and validated by pydantic.
"""

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class TradingMode(str, Enum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"
    PAPER = "paper"
    BACKTEST = "backtest"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_name: str = "trading-bot"
    app_env: AppEnv = AppEnv.DEVELOPMENT
    app_debug: bool = True
    log_level: str = "INFO"

    # --- API / security ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    jwt_secret_key: str = Field(default="dev-only-insecure-secret")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    credential_encryption_key: str = Field(default="")
    two_factor_issuer: str = "TradingBot"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://trading_bot:change-me@localhost:5432/trading_bot"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Broker: MetaTrader 5 ---
    mt5_enabled: bool = False
    mt5_login: str = ""
    mt5_password: str = ""
    mt5_investor_password: str = ""
    mt5_server: str = ""
    mt5_broker: str = ""

    # --- Broker: MetaTrader 4 (via bridge) ---
    mt4_enabled: bool = False
    mt4_bridge_host: str = "127.0.0.1"
    mt4_bridge_port: int = 5555
    mt4_login: str = ""
    mt4_password: str = ""
    mt4_server: str = ""
    mt4_broker: str = ""

    # --- Trading defaults (overridable per-user in DB, Phase 2+) ---
    trading_mode: TradingMode = TradingMode.PAPER
    confidence_threshold: float = 90.0
    risk_per_trade_percent: float = 1.0
    max_daily_loss_percent: float = 3.0
    max_weekly_loss_percent: float = 6.0
    max_drawdown_percent: float = 10.0
    max_open_positions: int = 3
    max_trades_per_day: int = 10
    max_spread_points: float = 30.0
    max_slippage_points: float = 10.0
    daily_profit_target_percent: float = 2.0
    trade_news_blackout_minutes: int = 30

    # --- News engine ---
    economic_calendar_api_key: str = ""
    economic_calendar_base_url: str = ""
    news_trading_enabled: bool = False

    # --- Notifications ---
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email_from: str = ""
    notify_email_to: str = ""

    # --- Monitoring ---
    sentry_dsn: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == AppEnv.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return a cached, process-wide Settings instance."""
    return Settings()
