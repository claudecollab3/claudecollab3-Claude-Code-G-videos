"""Query layer for per-user TradingConfig."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.trading_config import TradingConfig


class TradingConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_user(self, user_id: uuid.UUID) -> TradingConfig | None:
        result = await self.db.execute(
            select(TradingConfig).where(TradingConfig.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_user(self, user_id: uuid.UUID) -> TradingConfig:
        config = await self.get_for_user(user_id)
        if config is not None:
            return config
        config = TradingConfig(user_id=user_id)
        self.db.add(config)
        await self.db.flush()
        await self.db.refresh(config)
        return config
