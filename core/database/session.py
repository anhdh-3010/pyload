from contextvars import ContextVar, Token
from datetime import datetime
from urllib.parse import quote_plus

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid, uuid7

from core.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str | None:
    return session_context.get(None)


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


# URL-encode the password to handle special characters
encoded_password = quote_plus(config.postgres_password)
POSTGRES_URL: str = f"postgresql+asyncpg://{config.postgres_user}:{encoded_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_db}"

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
)

# Create scoped session
async_session: async_scoped_session[AsyncSession] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)


async def get_unit_of_work():
    """
    Get a Unit of Work instance for repository management.

    Works in conjunction with SQLAlchemyMiddleware which handles:
    - Session creation per request
    - Transaction boundaries (begin/commit/rollback)
    - Session cleanup

    UoW responsibility:
    - Repository management
    - Identity map consistency
    - Change aggregation

    :return: UnitOfWork instance
    """
    from core.unit_of_work import UnitOfWork

    session = async_session()
    try:
        yield UnitOfWork(session)
    finally:
        await async_session.remove()


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
