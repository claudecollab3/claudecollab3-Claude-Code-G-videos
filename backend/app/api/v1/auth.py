"""Registration, login (with optional 2FA), token refresh/revocation, and
2FA enrollment endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from authentication.jwt import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_token_expiry,
)
from authentication.password import hash_password, verify_password
from authentication.rate_limit import RateLimiter
from authentication.totp import generate_totp_secret, get_provisioning_uri, verify_totp_code
from backend.app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    TOTPCodeRequest,
    TOTPSetupResponse,
)
from backend.app.schemas.user import UserResponse
from database.models.user import User
from database.repositories.audit_repository import AuditRepository
from database.repositories.session_repository import SessionRepository
from database.repositories.user_repository import UserRepository
from database.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _as_aware_utc(value: datetime) -> datetime:
    """SQLite (used in tests) drops tzinfo on round-trip; Postgres keeps it.
    Normalize so expiry comparisons work against either backend."""
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


_login_rate_limit = RateLimiter(scope="login", limit=5, window_seconds=60)
_register_rate_limit = RateLimiter(scope="register", limit=5, window_seconds=300)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_register_rate_limit),
) -> UserResponse:
    users = UserRepository(db)
    if await users.get_by_email(payload.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = await users.create(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    await AuditRepository(db).record(
        action="user.register",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return UserResponse.model_validate(user)


async def _issue_token_pair(*, db: AsyncSession, user: User, request: Request) -> TokenResponse:
    access_token = create_access_token(user_id=user.id, role=user.role)
    raw_refresh_token = generate_refresh_token()

    await SessionRepository(db).create(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=refresh_token_expiry(),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_login_rate_limit),
) -> TokenResponse:
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )

    users = UserRepository(db)
    user = await users.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise invalid_credentials

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    if user.totp_enabled:
        if (
            not user.totp_secret
            or not payload.totp_code
            or not verify_totp_code(secret=user.totp_secret, code=payload.totp_code)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing 2FA code"
            )

    await AuditRepository(db).record(
        action="user.login",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return await _issue_token_pair(db=db, user=user, request=request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    invalid_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
    )

    sessions = SessionRepository(db)
    token_hash = hash_refresh_token(payload.refresh_token)
    session = await sessions.get_by_token_hash(token_hash)

    if session is None or not session.is_active:
        raise invalid_token
    if _as_aware_utc(session.expires_at) < datetime.now(UTC):
        raise invalid_token

    user = await UserRepository(db).get_by_id(session.user_id)
    if user is None or not user.is_active:
        raise invalid_token

    # Rotate: revoke the used refresh token and issue a fresh pair.
    await sessions.revoke(session)
    return await _issue_token_pair(db=db, user=user, request=request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)) -> None:
    sessions = SessionRepository(db)
    session = await sessions.get_by_token_hash(hash_refresh_token(payload.refresh_token))
    if session is not None and session.is_active:
        await sessions.revoke(session)


@router.post("/2fa/setup", response_model=TOTPSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> TOTPSetupResponse:
    secret = generate_totp_secret()
    current_user.totp_secret = secret
    current_user.totp_enabled = False
    await db.flush()

    return TOTPSetupResponse(
        secret=secret,
        provisioning_uri=get_provisioning_uri(secret=secret, account_email=current_user.email),
    )


@router.post("/2fa/enable", response_model=UserResponse)
async def enable_2fa(
    payload: TOTPCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Call /auth/2fa/setup first"
        )
    if not verify_totp_code(secret=current_user.totp_secret, code=payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    current_user.totp_enabled = True
    await db.flush()
    await AuditRepository(db).record(action="user.2fa_enabled", user_id=current_user.id)
    return UserResponse.model_validate(current_user)


@router.post("/2fa/disable", response_model=UserResponse)
async def disable_2fa(
    payload: TOTPCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    if not current_user.totp_enabled or not current_user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not enabled")
    if not verify_totp_code(secret=current_user.totp_secret, code=payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    current_user.totp_enabled = False
    current_user.totp_secret = None
    await db.flush()
    await AuditRepository(db).record(action="user.2fa_disabled", user_id=current_user.id)
    return UserResponse.model_validate(current_user)
