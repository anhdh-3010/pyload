from uuid import UUID

from sqlalchemy import select

from core.repository.base import BaseRepository
from modules.download_tasks.domain.models import DownloadTask


class DownloadTaskRepository(BaseRepository[DownloadTask]):
    model_class = DownloadTask

    async def get_by_id_for_update(self, task_id: UUID) -> DownloadTask | None:
        result = await self.session.execute(
            select(DownloadTask).where(DownloadTask.id == task_id).with_for_update()
        )
        return result.scalar_one_or_none()
