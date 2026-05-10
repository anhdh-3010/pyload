from typing import Annotated

from fastapi import Depends

from core import UnitOfWork, get_unit_of_work

from .services import DownloadTaskService


def get_download_task_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> DownloadTaskService:
    """Dependency to get DownloadTaskService instance with UnitOfWork."""
    return DownloadTaskService(uow)


DownloadTaskServiceDep = Annotated[DownloadTaskService, Depends(get_download_task_service)]
