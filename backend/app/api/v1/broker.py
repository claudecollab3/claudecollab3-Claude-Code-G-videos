"""Broker credential management and connection testing."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from backend.app.schemas.broker import (
    AccountInfoResponse,
    BrokerCredentialCreateRequest,
    BrokerCredentialResponse,
    InstrumentResponse,
)
from broker.adapter import BrokerConnectionError
from broker.credentials import connect_with_backoff, encrypt_broker_secret
from broker.factory import build_adapter
from broker.instruments import DEFAULT_INSTRUMENTS
from database.models.user import User
from database.repositories.audit_repository import AuditRepository
from database.repositories.broker_credential_repository import BrokerCredentialRepository
from database.session import get_db

router = APIRouter(prefix="/broker", tags=["broker"])


@router.get("/instruments", response_model=list[InstrumentResponse])
async def list_instruments() -> list[InstrumentResponse]:
    return [InstrumentResponse(**vars(i)) for i in DEFAULT_INSTRUMENTS]


@router.post(
    "/credentials", response_model=BrokerCredentialResponse, status_code=status.HTTP_201_CREATED
)
async def create_credential(
    payload: BrokerCredentialCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrokerCredentialResponse:
    credential = await BrokerCredentialRepository(db).create(
        user_id=current_user.id,
        broker_type=payload.broker_type,
        broker_name=payload.broker_name,
        server=payload.server,
        login=payload.login,
        encrypted_password=encrypt_broker_secret(payload.password),
        encrypted_investor_password=(
            encrypt_broker_secret(payload.investor_password) if payload.investor_password else None
        ),
    )
    await AuditRepository(db).record(
        action="broker_credential.create",
        user_id=current_user.id,
        resource=str(credential.id),
        detail={"broker_type": payload.broker_type.value},
    )
    return BrokerCredentialResponse.model_validate(credential)


@router.get("/credentials", response_model=list[BrokerCredentialResponse])
async def list_credentials(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[BrokerCredentialResponse]:
    credentials = await BrokerCredentialRepository(db).list_for_user(current_user.id)
    return [BrokerCredentialResponse.model_validate(c) for c in credentials]


@router.delete("/credentials/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = BrokerCredentialRepository(db)
    credential = await repo.get_for_user(credential_id, current_user.id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    await repo.delete(credential)


@router.post("/credentials/{credential_id}/connect", response_model=AccountInfoResponse)
async def test_connection(
    credential_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AccountInfoResponse:
    credential = await BrokerCredentialRepository(db).get_for_user(credential_id, current_user.id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    adapter = build_adapter(credential)
    try:
        await connect_with_backoff(adapter)
        account_info = await adapter.get_account_info()
    except BrokerConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    finally:
        await adapter.disconnect()

    await AuditRepository(db).record(
        action="broker_credential.connect_test",
        user_id=current_user.id,
        resource=str(credential.id),
    )
    return AccountInfoResponse(**vars(account_info))
