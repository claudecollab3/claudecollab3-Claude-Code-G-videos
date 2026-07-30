"""Query layer for encrypted BrokerCredential records."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.broker_credential import BrokerCredential, BrokerType


class BrokerCredentialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        broker_type: BrokerType,
        broker_name: str,
        server: str,
        login: str,
        encrypted_password: str,
        encrypted_investor_password: str | None = None,
    ) -> BrokerCredential:
        credential = BrokerCredential(
            user_id=user_id,
            broker_type=broker_type,
            broker_name=broker_name,
            server=server,
            login=login,
            encrypted_password=encrypted_password,
            encrypted_investor_password=encrypted_investor_password,
        )
        self.db.add(credential)
        await self.db.flush()
        await self.db.refresh(credential)
        return credential

    async def get_for_user(
        self, credential_id: uuid.UUID, user_id: uuid.UUID
    ) -> BrokerCredential | None:
        result = await self.db.execute(
            select(BrokerCredential).where(
                BrokerCredential.id == credential_id, BrokerCredential.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[BrokerCredential]:
        result = await self.db.execute(
            select(BrokerCredential)
            .where(BrokerCredential.user_id == user_id)
            .order_by(BrokerCredential.created_at)
        )
        return list(result.scalars().all())

    async def delete(self, credential: BrokerCredential) -> None:
        await self.db.delete(credential)
        await self.db.flush()
