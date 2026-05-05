from typing import Annotated

from fastapi import Depends

from core import UnitOfWork, get_unit_of_work

from .services import UserService


def get_user_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> UserService:
    """Dependency to get UserService instance with UnitOfWork"""
    return UserService(uow)


# Type aliases for cleaner router signatures
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
