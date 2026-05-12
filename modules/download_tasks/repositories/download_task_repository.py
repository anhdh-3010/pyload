from core.repository.base import BaseRepository
from modules.download_tasks.domain.models import DownloadTask


class DownloadTaskRepository(BaseRepository[DownloadTask]):
    model_class = DownloadTask
