"""Current-user profile and admin user management."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from authentication.rbac import require_admin
from backend.app.schemas.user import UserResponse, UserUpdateRequest
from database.models.user import User
from database.repositories.user_repository import UserRepository
from database.session import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    await db.flush()
    return UserResponse.model_validate(current_user)


@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
async def list_users(
    limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)
) -> list[UserResponse]:
    users = await UserRepository(db).list_all(limit=limit, offset=offset)
    return [UserResponse.model_validate(u) for u in users]
