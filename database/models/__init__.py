"""Import every model so `Base.metadata` sees all tables (for Alembic
autogenerate and for `Base.metadata.create_all` in tests)."""

from database.models.audit_log import AuditLog
from database.models.broker_credential import BrokerCredential, BrokerType
from database.models.market_data import Candle, Timeframe
from database.models.trading_config import TradingConfig
from database.models.user import Role, User
from database.models.user_session import UserSession

__all__ = [
    "AuditLog",
    "BrokerCredential",
    "BrokerType",
    "Candle",
    "Timeframe",
    "TradingConfig",
    "Role",
    "User",
    "UserSession",
]
