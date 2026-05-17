import uuid

from fastapi import status

from core import NotFoundException, UnitOfWork
from core.exceptions import CustomException
from core.utils import to_jsonable, utcnow
from modules.download_tasks.domain.enums import DownloadStatus
from modules.download_tasks.domain.models import DownloadTask
from modules.download_tasks.domain.schemas import (
    CreateDownloadTaskRequest,
    UpdateDownloadTaskRequest,
)
from modules.download_tasks.repositories.download_task_repository import DownloadTaskRepository
from modules.outbox.repositories.outbox_repository import OutboxEventRepository


class DownloadTaskAccessError(CustomException):
    code = status.HTTP_404_NOT_FOUND
    message = "Download task not found"


class DownloadTaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_task(
        self,
        account_id: uuid.UUID,
        request: CreateDownloadTaskRequest,
    ) -> DownloadTask:
        download_task_repo = self.uow.get_repository(DownloadTaskRepository)
        outbox_event_repo = self.uow.get_repository(OutboxEventRepository)
        task = await download_task_repo.create(
            {
                "account_id": account_id,
                "download_type": request.download_type,
                "url": str(request.url),
                "download_status": DownloadStatus.PENDING,
                "attempts": 0,
                "max_attempts": 3,
                "run_at": utcnow(),
                "task_metadata": request.metadata,
            }
        )

        await outbox_event_repo.create(
            {
                "aggregate_type": "download_task",
                "aggregate_id": task.id,
                "event_type": "download_task.created",
                "payload": to_jsonable(
                    {
                        "task_id": task.id,
                        "account_id": account_id,
                        "download_type": request.download_type,
                        "url": str(request.url),
                    }
                ),
            }
        )

        return task

    async def list_tasks(self, account_id: uuid.UUID) -> list[DownloadTask]:
        download_task_repo = self.uow.get_repository(DownloadTaskRepository)
        tasks = await download_task_repo.filter(
            filter_conditions=[DownloadTask.account_id == account_id]
        )
        return list(tasks or [])

    async def get_task(self, account_id: uuid.UUID, task_id: uuid.UUID) -> DownloadTask:
        return await self._get_owned_task(account_id, task_id)

    async def update_task(
        self,
        account_id: uuid.UUID,
        task_id: uuid.UUID,
        request: UpdateDownloadTaskRequest,
    ) -> DownloadTask:
        task = await self._get_owned_task(account_id, task_id)
        download_task_repo = self.uow.get_repository(DownloadTaskRepository)

        update_data: dict = {}
        if request.download_type is not None:
            update_data["download_type"] = request.download_type
        if request.url is not None:
            update_data["url"] = str(request.url)
        if request.metadata is not None:
            update_data["task_metadata"] = request.metadata

        if not update_data:
            return task

        updated_task = await download_task_repo.update(task.id, update_data)
        if updated_task is None:
            raise NotFoundException("Download task not found")

        return updated_task

    async def delete_task(self, account_id: uuid.UUID, task_id: uuid.UUID) -> bool:
        task = await self._get_owned_task(account_id, task_id)
        download_task_repo = self.uow.get_repository(DownloadTaskRepository)
        return await download_task_repo.delete(task.id)

    async def _get_owned_task(
        self,
        account_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> DownloadTask:
        download_task_repo = self.uow.get_repository(DownloadTaskRepository)
        tasks = await download_task_repo.filter(
            filter_conditions=[
                DownloadTask.id == task_id,
                DownloadTask.account_id == account_id,
            ]
        )

        if not tasks:
            raise DownloadTaskAccessError()

        return tasks[0]
