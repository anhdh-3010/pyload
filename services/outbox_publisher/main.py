import asyncio
import logging

from core import config
from core.kafka.producer import KafkaProducer
from modules.outbox.services.publisher import OutboxPublisherService

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    producer = KafkaProducer(config.kafka_bootstrap_servers)
    service = OutboxPublisherService(producer)

    await producer.start()
    try:
        await service.run_forever()
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
