from app.api.v1.download_tasks.domain.models import OutboxEvent
from core.repository.base import BaseRepository


class OutboxEventRepository(BaseRepository[OutboxEvent]):
    model_class = OutboxEvent
