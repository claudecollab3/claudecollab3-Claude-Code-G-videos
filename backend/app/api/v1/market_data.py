"""Historical OHLCV lookup and on-demand ingestion from a user's broker."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from backend.app.schemas.market_data import CandleResponse, SyncMarketDataRequest
from broker.adapter import BrokerConnectionError
from broker.credentials import connect_with_backoff
from broker.factory import build_adapter
from broker.ingestion import DEFAULT_TIMEFRAMES, MarketDataIngestionService
from database.models.market_data import Timeframe
from database.models.user import User
from database.repositories.broker_credential_repository import BrokerCredentialRepository
from database.repositories.market_data_repository import MarketDataRepository
from database.session import get_db

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/candles", response_model=list[CandleResponse])
async def get_candles(
    symbol: str,
    timeframe: Timeframe,
    limit: int = Query(default=200, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
) -> list[CandleResponse]:
    candles = await MarketDataRepository(db).get_latest(symbol.upper(), timeframe, limit=limit)
    return [CandleResponse.model_validate(c) for c in candles]


@router.post("/sync")
async def sync_market_data(
    payload: SyncMarketDataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    try:
        credential_id = uuid.UUID(payload.broker_credential_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid broker_credential_id"
        ) from exc

    credential = await BrokerCredentialRepository(db).get_for_user(credential_id, current_user.id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    adapter = build_adapter(credential)
    try:
        await connect_with_backoff(adapter)
        service = MarketDataIngestionService(adapter=adapter, db=db)
        return await service.sync_symbol(
            payload.symbol.upper(),
            timeframes=tuple(payload.timeframes) if payload.timeframes else DEFAULT_TIMEFRAMES,
            count=payload.count,
        )
    except BrokerConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    finally:
        await adapter.disconnect()
