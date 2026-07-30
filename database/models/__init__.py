"""Import every model so `Base.metadata` sees all tables (for Alembic
autogenerate and for `Base.metadata.create_all` in tests)."""

from database.models.ai_prediction import AIPrediction
from database.models.audit_log import AuditLog
from database.models.broker_credential import BrokerCredential, BrokerType
from database.models.market_data import Candle, Timeframe
from database.models.news_event import NewsEvent, NewsImpact
from database.models.trading_config import TradingConfig
from database.models.user import Role, User
from database.models.user_session import UserSession

__all__ = [
    "AIPrediction",
    "AuditLog",
    "BrokerCredential",
    "BrokerType",
    "Candle",
    "Timeframe",
    "NewsEvent",
    "NewsImpact",
    "TradingConfig",
    "Role",
    "User",
    "UserSession",
]
