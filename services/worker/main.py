import asyncio
import logging

import core.models  # noqa: F401
from core import config
from core.kafka.consumer import KafkaConsumer
from services.worker.service import WorkerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    consumer = KafkaConsumer(
        bootstrap_servers=config.kafka_bootstrap_servers,
        topic=config.kafka_download_task_ready_topic,
        group_id=config.kafka_worker_group_id,
    )
    service = WorkerService()

    await consumer.start()
    logger.info(
        "Worker service started. topic=%s group_id=%s",
        config.kafka_download_task_ready_topic,
        config.kafka_worker_group_id,
    )

    try:
        async for message in consumer.raw():
            try:
                await service.process_download_task_ready(message.value)
                await consumer.raw().commit()
            except KeyError:
                logger.exception("Invalid Kafka payload: %s", message.value)
                await consumer.raw().commit()
            except Exception:
                logger.exception(
                    "Worker failed while handling Kafka message at offset=%s",
                    message.offset,
                )
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
