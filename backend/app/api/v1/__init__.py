from fastapi import APIRouter

from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.backtesting import router as backtesting_router
from backend.app.api.v1.broker import router as broker_router
from backend.app.api.v1.decision import router as decision_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.market_data import router as market_data_router
from backend.app.api.v1.news import router as news_router
from backend.app.api.v1.notifications import router as notifications_router
from backend.app.api.v1.signals import router as signals_router
from backend.app.api.v1.strategies import router as strategies_router
from backend.app.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(broker_router)
api_router.include_router(market_data_router)
api_router.include_router(strategies_router)
api_router.include_router(signals_router)
api_router.include_router(ai_router)
api_router.include_router(news_router)
api_router.include_router(decision_router)
api_router.include_router(backtesting_router)
api_router.include_router(notifications_router)
