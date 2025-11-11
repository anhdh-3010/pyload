from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    is_admin: bool = False
    current_cefr_level: Optional[str] = None
    learning_goal: Optional[str] = None
    time_per_day_minutes: int = 30
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenWithUser(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
