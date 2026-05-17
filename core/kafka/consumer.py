from aiokafka import AIOKafkaConsumer

from core.utils import loads_json


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._group_id = group_id
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            enable_auto_commit=False,
            value_deserializer=loads_json,
            key_deserializer=lambda value: value.decode("utf-8") if value else None,
        )

        await self._consumer.start()

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()

    def raw(self) -> AIOKafkaConsumer:
        if self._consumer is None:
            raise RuntimeError("Kafka consumer is not started")

        return self._consumer
