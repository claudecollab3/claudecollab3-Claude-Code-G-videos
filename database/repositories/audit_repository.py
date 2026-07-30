"""Write-mostly access to the audit trail."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(
        self,
        *,
        action: str,
        user_id: uuid.UUID | None = None,
        resource: str | None = None,
        detail: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=action,
            user_id=user_id,
            resource=resource,
            detail=detail,
            ip_address=ip_address,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry
