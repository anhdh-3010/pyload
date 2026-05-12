import asyncio
import logging

from core import UnitOfWork, config, create_session_manager
from core.kafka.producer import KafkaProducer
from modules.outbox.domain.models import OutboxEvent
from modules.outbox.repositories.outbox_repository import OutboxEventRepository

logger = logging.getLogger(__name__)


class OutboxPublisherService:
    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    async def run_forever(self) -> None:
        while True:
            published_count = await self.run_once()
            if published_count == 0:
                await asyncio.sleep(config.outbox_poll_interval_seconds)

    async def run_once(self) -> int:
        async with create_session_manager() as session, UnitOfWork(session) as uow:
            outbox_repo = uow.get_repository(OutboxEventRepository)
            events = await outbox_repo.fetch_unpublished_events(limit=config.outbox_batch_size)

            if not events:
                return 0

            for event in events:
                await self._publish_event(event)
                await outbox_repo.mark_as_published(event)

            logger.info("Published %s outbox event(s)", len(events))
            return len(events)

    async def _publish_event(self, event: OutboxEvent) -> None:
        await self.producer.publish(
            topic=self._resolve_topic(event),
            key=str(event.aggregate_id),
            value=event.payload,
        )

    def _resolve_topic(self, event: OutboxEvent) -> str:
        if event.aggregate_type == "download_task":
            return config.kafka_download_tasks_topic

        return event.aggregate_type
