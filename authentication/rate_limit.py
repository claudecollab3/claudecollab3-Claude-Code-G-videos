"""Redis-backed fixed-window rate limiting for sensitive endpoints
(login, register, 2FA verify) to slow down credential-stuffing / brute force.
"""

from functools import lru_cache

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from config import get_settings


@lru_cache
def get_redis() -> redis.Redis:
    return redis.from_url(get_settings().redis_url, decode_responses=True)


class RateLimiter:
    """Call as a FastAPI dependency: `Depends(RateLimiter(scope="login", limit=5, window_seconds=60))`."""

    def __init__(self, *, scope: str, limit: int, window_seconds: int):
        self.scope = scope
        self.limit = limit
        self.window_seconds = window_seconds

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{self.scope}:{client_ip}"

        client = get_redis()
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, self.window_seconds)

        if count > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, please try again later.",
            )
