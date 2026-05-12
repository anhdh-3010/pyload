from datetime import UTC, datetime

from sqlalchemy import select

from core.repository.base import BaseRepository
from modules.outbox.domain.models import OutboxEvent


class OutboxEventRepository(BaseRepository[OutboxEvent]):
    model_class = OutboxEvent

    async def fetch_unpublished_events(self, limit: int = 100) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.id.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        return list(result.scalars().all())

    async def mark_as_published(self, event: OutboxEvent) -> OutboxEvent:
        event.published_at = datetime.now(UTC)
        await self.session.flush()
        return event
