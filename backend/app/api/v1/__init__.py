from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.broker import router as broker_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.market_data import router as market_data_router
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
