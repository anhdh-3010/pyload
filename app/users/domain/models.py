from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from core import Base
from core.database.timestamp import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
