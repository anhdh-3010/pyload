from typing import Annotated

from fastapi import Depends

from core import UnitOfWork, get_unit_of_work
from modules.accounts.domain.services import AccountService


def get_account_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> AccountService:
    return AccountService(uow)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
