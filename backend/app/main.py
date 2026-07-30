"""FastAPI application entrypoint.

Run with: uvicorn backend.app.main:app --reload
"""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1 import api_router
from backend.app.core.logging import configure_logging, get_logger
from config import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    logger.info(
        "startup",
        app_env=settings.app_env.value,
        trading_mode=settings.trading_mode.value,
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    settings.assert_production_ready()

    app = FastAPI(
        title="Trading Bot API",
        description="AI-driven Forex & Crypto trading system",
        version="0.1.0",
        # Production never runs in debug mode (stack traces in error
        # responses) even if APP_DEBUG is left at its dev-friendly default.
        debug=settings.app_debug and not settings.is_production,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not settings.is_production else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

    app.include_router(api_router)

    return app


app = create_app()
