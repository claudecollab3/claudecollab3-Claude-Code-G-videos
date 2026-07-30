"""Query layer for the notification dispatch audit trail."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.notification_log import NotificationLog


class NotificationLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID | None,
        event: str,
        channel: str,
        success: bool,
        title: str,
        body: str,
    ) -> NotificationLog:
        entry = NotificationLog(
            user_id=user_id, event=event, channel=channel, success=success, title=title, body=body
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def list_recent(self, user_id: uuid.UUID, *, limit: int = 50) -> list[NotificationLog]:
        result = await self.db.execute(
            select(NotificationLog)
            .where(NotificationLog.user_id == user_id)
            .order_by(NotificationLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
