"""Notification preferences, test dispatch, history, and the WebSocket
bridge for in-app (desktop/push) delivery."""

import asyncio

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from authentication.jwt import TokenError, decode_access_token
from backend.app.schemas.notifications import (
    NotificationLogResponse,
    NotificationPreferencesResponse,
    NotificationResultResponse,
    TestNotificationRequest,
    UpdateNotificationPreferenceRequest,
)
from database.models.user import User
from database.repositories.notification_log_repository import NotificationLogRepository
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db
from notifications.dispatcher import DEFAULT_ENABLED_CHANNELS, NotificationDispatcher
from notifications.events import NotificationMessage
from notifications.hub import get_hub

router = APIRouter(prefix="/notifications", tags=["notifications"])

_dispatcher = NotificationDispatcher()


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> NotificationPreferencesResponse:
    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    merged = {**DEFAULT_ENABLED_CHANNELS, **(config.notification_channels or {})}
    return NotificationPreferencesResponse(channels=merged)


@router.patch("/preferences", response_model=NotificationPreferencesResponse)
async def update_preferences(
    payload: UpdateNotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferencesResponse:
    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    channels = dict(config.notification_channels or {})
    channels[payload.channel] = payload.enabled
    config.notification_channels = channels
    await db.flush()

    merged = {**DEFAULT_ENABLED_CHANNELS, **channels}
    return NotificationPreferencesResponse(channels=merged)


@router.post("/test", response_model=list[NotificationResultResponse])
async def send_test_notification(
    payload: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationResultResponse]:
    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    message = NotificationMessage(event=payload.event, title=payload.title, body=payload.body)

    results = await _dispatcher.dispatch(
        message,
        enabled_channels=config.notification_channels or {},
        user_id=current_user.id,
        db=db,
    )
    return [NotificationResultResponse(channel=r.channel, success=r.success) for r in results]


@router.get("/history", response_model=list[NotificationLogResponse])
async def notification_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[NotificationLogResponse]:
    logs = await NotificationLogRepository(db).list_recent(current_user.id)
    return [
        NotificationLogResponse(
            event=log.event,
            channel=log.channel,
            success=log.success,
            title=log.title,
            body=log.body,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket, token: str = Query(...)) -> None:
    try:
        decode_access_token(token)
    except TokenError:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    hub = get_hub()
    queue = hub.subscribe()

    try:
        while True:
            message = await queue.get()
            await websocket.send_json(
                {
                    "event": message.event.value,
                    "title": message.title,
                    "body": message.body,
                    "data": message.data,
                }
            )
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        hub.unsubscribe(queue)
