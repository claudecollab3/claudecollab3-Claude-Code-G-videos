import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from database.models.user import Role


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None
    role: Role
    is_active: bool
    is_verified: bool
    totp_enabled: bool
    created_at: datetime


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
