from app.api.v1.download_tasks.domain.models import DownloadTask
from core.repository.base import BaseRepository


class DownloadTaskRepository(BaseRepository[DownloadTask]):
    model_class = DownloadTask
