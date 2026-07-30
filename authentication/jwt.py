"""JWT access tokens + opaque refresh tokens.

Access tokens are short-lived signed JWTs (stateless, verified via
signature). Refresh tokens are long, random opaque strings — only a SHA-256
hash of the token is ever persisted (see `database.models.UserSession`), so a
stolen database dump does not yield usable refresh tokens, and a session can
be revoked ("log out this device") without needing to blocklist a JWT.
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from config import get_settings
from database.models.user import Role


class TokenError(Exception):
    """Raised when a JWT is missing, malformed, expired, or has the wrong type."""


@dataclass
class AccessTokenPayload:
    user_id: uuid.UUID
    role: Role
    expires_at: datetime


def create_access_token(*, user_id: uuid.UUID, role: Role) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> AccessTokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError("Invalid or expired access token") from exc

    if payload.get("type") != "access":
        raise TokenError("Token is not an access token")

    try:
        user_id = uuid.UUID(payload["sub"])
        role = Role(payload["role"])
        expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    except (KeyError, ValueError) as exc:
        raise TokenError("Malformed access token payload") from exc

    return AccessTokenPayload(user_id=user_id, role=role, expires_at=expires_at)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    settings = get_settings()
    return datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
