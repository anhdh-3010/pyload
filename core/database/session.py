from contextvars import ContextVar, Token
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB

from core.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


# URL-encode the password to handle special characters
encoded_password = quote_plus(config.postgres_password)
POSTGRES_URL: str = (
    f"postgresql+asyncpg://{config.postgres_user}:{encoded_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"
)

# Create async engine for SQLAlchemy 2.0
engine: AsyncEngine = create_async_engine(
    POSTGRES_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Create scoped session
async_session: async_scoped_session[AsyncSession] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)


async def get_async_session():
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    try:
        yield async_session
    finally:
        await async_session.close()


class Base(DeclarativeBase):
    # Cấu hình để SQLAlchemy hiểu kiểu dữ liệu JSONB
    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[dict[str, Any]]: JSONB,
    }
