from typing import Optional
import uuid

from sqlalchemy import TEXT, UUID, Boolean, Integer, String
from app.core.database.timestamp import TimestampMixin
from app.core.database.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    current_cefr_level: Mapped[Optional[str]] = mapped_column(String(10))
    learning_goal: Mapped[Optional[str]] = mapped_column(TEXT)
    time_per_day_minutes: Mapped[int] = mapped_column(Integer, server_default="30")
