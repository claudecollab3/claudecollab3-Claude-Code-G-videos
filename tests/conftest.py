import fakeredis.aioredis
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import authentication.rate_limit as rate_limit

# Import models so their tables register on Base.metadata before create_all.
import database.models  # noqa: F401
from backend.app.main import app
from database.base import Base
from database.session import get_db

# Auth endpoints are rate-limited via Redis; use an in-memory fake so tests
# don't require a live Redis server.
rate_limit.get_redis.cache_clear()
_fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
rate_limit.get_redis = lambda: _fake_redis

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)


async def _override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture(autouse=True)
async def _prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _fake_redis.flushall()
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
