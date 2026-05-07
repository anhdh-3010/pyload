from typing import Annotated

from fastapi import Depends

from core import UnitOfWork, get_unit_of_work

from .services import AccountService


def get_account_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> AccountService:
    """Dependency to get AccountService instance with UnitOfWork"""
    return AccountService(uow)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
