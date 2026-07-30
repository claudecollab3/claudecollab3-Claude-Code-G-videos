"""Role-based access control dependency factory."""

from fastapi import Depends, HTTPException, status

from authentication.dependencies import get_current_user
from database.models.user import Role, User


def require_role(*allowed_roles: Role):
    """FastAPI dependency: 403s unless the current user has one of `allowed_roles`."""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return checker


require_admin = require_role(Role.ADMIN)
