"""Query layer for UserSession (refresh-token records)."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_session import UserSession


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_token_hash(self, refresh_token_hash: str) -> UserSession | None:
        result = await self.db.execute(
            select(UserSession).where(UserSession.refresh_token_hash == refresh_token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, session: UserSession) -> None:
        session.revoked_at = datetime.utcnow()
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.user_id == user_id, UserSession.revoked_at.is_(None)
            )
        )
        for session in result.scalars().all():
            session.revoked_at = datetime.utcnow()
        await self.db.flush()
