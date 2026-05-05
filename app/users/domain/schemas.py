import uuid
from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    avatar: str | None = None
    is_admin: bool = False
    current_cefr_level: str | None = None
    learning_goal: str | None = None
    time_per_day_minutes: int = 30
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenWithUser(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
