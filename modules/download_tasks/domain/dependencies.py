from typing import Annotated

from fastapi import Depends

from core import UnitOfWork, get_unit_of_work
from modules.download_tasks.domain.services import DownloadTaskService


def get_download_task_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> DownloadTaskService:
    return DownloadTaskService(uow)


DownloadTaskServiceDep = Annotated[DownloadTaskService, Depends(get_download_task_service)]
