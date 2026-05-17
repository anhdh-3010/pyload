import asyncio
import logging

from core import UnitOfWork, config
from core.database.session import async_session_factory
from core.utils import to_jsonable, utcnow
from modules.download_tasks.domain.enums import DownloadStatus
from modules.download_tasks.domain.models import DownloadTask
from modules.download_tasks.domain.state_machine import ensure_can_transition
from modules.download_tasks.repositories.download_task_repository import DownloadTaskRepository
from modules.outbox.repositories.outbox_repository import OutboxEventRepository

logger = logging.getLogger(__name__)


class SchedulerService:
    async def run_forever(self) -> None:
        while True:
            scheduled_count = await self.run_once()
            if scheduled_count == 0:
                await asyncio.sleep(config.scheduler_poll_interval_seconds)

    async def run_once(self) -> int:
        now = utcnow()
        async with async_session_factory() as session, UnitOfWork(session) as uow:
            task_repo = uow.get_repository(DownloadTaskRepository)
            outbox_repo = uow.get_repository(OutboxEventRepository)
            tasks = await task_repo.fetch_ready_for_scheduling(
                now=now,
                limit=config.scheduler_batch_size,
            )

            if not tasks:
                return 0

            for task in tasks:
                await self._schedule_task(task, outbox_repo)

            logger.info("Scheduled %s download task(s)", len(tasks))
            return len(tasks)

    async def _schedule_task(
        self,
        task: DownloadTask,
        outbox_repo: OutboxEventRepository,
    ) -> None:
        current_status = DownloadStatus(task.download_status)
        if current_status is DownloadStatus.PENDING:
            ensure_can_transition(current_status, DownloadStatus.SCHEDULED)
        elif current_status is DownloadStatus.PROCESSING and task.attempts >= task.max_attempts:
            ensure_can_transition(current_status, DownloadStatus.FAILED)
            task.download_status = DownloadStatus.FAILED
            task.locked_by = None
            task.locked_until = None
            return
        elif current_status is DownloadStatus.PROCESSING:
            ensure_can_transition(current_status, DownloadStatus.SCHEDULED)
        else:
            return

        task.download_status = DownloadStatus.SCHEDULED
        task.locked_by = None
        task.locked_until = None
        await outbox_repo.create(
            {
                "aggregate_type": "download_task",
                "aggregate_id": task.id,
                "event_type": "download_task.ready",
                "payload": to_jsonable(
                    {
                        "task_id": task.id,
                        "account_id": task.account_id,
                        "download_type": task.download_type,
                        "url": task.url,
                    }
                ),
            }
        )
