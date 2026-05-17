import logging
from pathlib import Path
from uuid import UUID

from core import UnitOfWork, config
from core.database.session import async_session_factory
from core.utils import to_jsonable, utcnow
from modules.download_tasks.domain.enums import DownloadStatus, DownloadType
from modules.download_tasks.domain.models import DownloadTask
from modules.download_tasks.domain.state_machine import ensure_can_transition
from modules.download_tasks.repositories.download_task_repository import DownloadTaskRepository
from services.worker.downloaders import BaseDownloader, DirectHttpDownloader

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(self):
        self._download_dir = Path(config.worker_download_dir)
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._downloaders: dict[DownloadType, BaseDownloader] = {
            DownloadType.DIRECT_HTTP: DirectHttpDownloader(self._download_dir),
        }

    async def process_download_task_created(self, payload: dict) -> None:
        task_id = UUID(str(payload["task_id"]))

        claimed_task = await self._claim_task(task_id)
        if claimed_task is None:
            logger.warning("Download task %s not found", task_id)
            return

        if not claimed_task.claimed:
            logger.info(
                "Skipping task %s because status is %s",
                task_id,
                DownloadStatus(claimed_task.task.download_status).name,
            )
            return

        try:
            task = claimed_task.task
            downloader = self._get_downloader(task)
            result = await downloader.download(task)
            await self._mark_task_success(task.id, result.file_path, result.file_size)
        except Exception as exc:
            logger.exception("Failed to process task %s", task.id)
            await self._mark_task_failed(task.id, str(exc))

    async def _claim_task(self, task_id: UUID) -> "ClaimedTask | None":
        async with async_session_factory() as session, UnitOfWork(session) as uow:
            repo = uow.get_repository(DownloadTaskRepository)
            task = await repo.get_by_id_for_update(task_id)
            if task is None:
                return None

            if DownloadStatus(task.download_status) is not DownloadStatus.PENDING:
                return ClaimedTask(task=task, claimed=False)

            ensure_can_transition(
                DownloadStatus(task.download_status),
                DownloadStatus.PROCESSING,
            )
            task.download_status = DownloadStatus.PROCESSING
            task.task_metadata = self._merge_metadata(
                task.task_metadata,
                {
                    "started_at": utcnow(),
                    "last_error": None,
                },
            )
            await session.flush()
            return ClaimedTask(task=task, claimed=True)

    async def _mark_task_success(
        self,
        task_id: UUID,
        file_path: Path,
        file_size: int,
    ) -> None:
        async with async_session_factory() as session, UnitOfWork(session) as uow:
            repo = uow.get_repository(DownloadTaskRepository)
            task = await repo.get_by_id_for_update(task_id)
            if task is None:
                logger.warning("Download task %s disappeared before success update", task_id)
                return

            ensure_can_transition(
                DownloadStatus(task.download_status),
                DownloadStatus.SUCCESS,
            )
            task.download_status = DownloadStatus.SUCCESS
            task.task_metadata = self._merge_metadata(
                task.task_metadata,
                {
                    "finished_at": utcnow(),
                    "file_path": str(file_path),
                    "file_size": file_size,
                    "last_error": None,
                },
            )
            await session.flush()

    async def _mark_task_failed(self, task_id: UUID, error_message: str) -> None:
        async with async_session_factory() as session, UnitOfWork(session) as uow:
            repo = uow.get_repository(DownloadTaskRepository)
            task = await repo.get_by_id_for_update(task_id)
            if task is None:
                logger.warning("Download task %s disappeared before failure update", task_id)
                return

            current_status = DownloadStatus(task.download_status)
            if current_status is DownloadStatus.FAILED:
                return

            ensure_can_transition(current_status, DownloadStatus.FAILED)
            task.download_status = DownloadStatus.FAILED
            task.task_metadata = self._merge_metadata(
                task.task_metadata,
                {
                    "finished_at": utcnow(),
                    "last_error": error_message,
                },
            )
            await session.flush()

    def _merge_metadata(self, current: dict | None, updates: dict) -> dict:
        merged = dict(current or {})
        merged.update(to_jsonable(updates))
        return merged

    def _get_downloader(self, task: DownloadTask) -> BaseDownloader:
        download_type = DownloadType(task.download_type)
        downloader = self._downloaders.get(download_type)
        if downloader is None:
            raise ValueError(f"Unsupported download type: {download_type.name}")
        return downloader


class ClaimedTask:
    def __init__(self, task: DownloadTask, claimed: bool):
        self.task = task
        self.claimed = claimed
