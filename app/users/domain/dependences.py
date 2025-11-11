from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..data_access.user_repository import UserRepository
from .services import UserService

from core import get_async_session


def get_user_repository(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    """Dependency to get UserRepository instance"""
    return UserRepository(db_session)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(user_repository)


# Type aliases for cleaner router signatures
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
