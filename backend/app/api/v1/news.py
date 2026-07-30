"""Economic calendar lookup and pre-trade news policy evaluation."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.news.factory import get_calendar_provider
from ai.news.policy import NewsPolicy
from authentication.dependencies import get_current_user
from backend.app.schemas.news import CalendarEventResponse, NewsPolicyRequest, NewsPolicyResponse
from database.models.user import User
from database.repositories.news_event_repository import NewsEventRepository
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db

router = APIRouter(prefix="/news", tags=["news"])


def _to_response(event) -> CalendarEventResponse:
    return CalendarEventResponse(
        external_id=event.external_id,
        name=event.name,
        currency=event.currency,
        impact=event.impact.value,
        event_time=event.event_time,
        forecast=event.forecast,
        previous=event.previous,
        actual=event.actual,
    )


@router.get("/upcoming", response_model=list[CalendarEventResponse])
async def upcoming_events(
    hours: int = 24, db: AsyncSession = Depends(get_db)
) -> list[CalendarEventResponse]:
    provider = get_calendar_provider()
    events = await provider.upcoming_events(hours_ahead=hours)

    repo = NewsEventRepository(db)
    for event in events:
        await repo.upsert(event)

    return [_to_response(e) for e in events]


@router.post("/policy", response_model=NewsPolicyResponse)
async def evaluate_news_policy(
    payload: NewsPolicyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NewsPolicyResponse:
    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)

    provider = get_calendar_provider()
    events = await provider.upcoming_events(hours_ahead=24)

    result = NewsPolicy().evaluate(
        events=events,
        now=datetime.now(UTC),
        news_trading_enabled=config.news_trading_enabled,
        blackout_minutes=config.trade_news_blackout_minutes,
        currency=payload.symbol[:3].upper(),
    )

    return NewsPolicyResponse(
        action=result.action.value,
        reason=result.reason,
        upcoming_event=_to_response(result.upcoming_event) if result.upcoming_event else None,
    )
