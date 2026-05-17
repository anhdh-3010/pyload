from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select

from core.repository.base import BaseRepository
from modules.download_tasks.domain.enums import DownloadStatus
from modules.download_tasks.domain.models import DownloadTask


class DownloadTaskRepository(BaseRepository[DownloadTask]):
    model_class = DownloadTask

    async def get_by_id_for_update(self, task_id: UUID) -> DownloadTask | None:
        result = await self.session.execute(
            select(DownloadTask).where(DownloadTask.id == task_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def fetch_ready_for_scheduling(
        self,
        now: datetime,
        limit: int,
    ) -> list[DownloadTask]:
        result = await self.session.execute(
            select(DownloadTask)
            .where(
                DownloadTask.run_at <= now,
                or_(
                    (
                        (DownloadTask.download_status == DownloadStatus.PENDING)
                        & (DownloadTask.attempts < DownloadTask.max_attempts)
                        & (DownloadTask.locked_until.is_(None) | (DownloadTask.locked_until < now))
                    ),
                    (
                        (DownloadTask.download_status == DownloadStatus.PROCESSING)
                        & DownloadTask.locked_until.is_not(None)
                        & (DownloadTask.locked_until < now)
                    ),
                ),
            )
            .order_by(DownloadTask.run_at.asc(), DownloadTask.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())
