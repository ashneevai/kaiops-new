import json
from aiokafka import AIOKafkaProducer

from app.core.config import settings


class KafkaPublisher:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def publish(self, topic: str, payload: dict) -> None:
        if not self._producer:
            raise RuntimeError("Kafka producer is not started")
        await self._producer.send_and_wait(topic, payload)


kafka_publisher = KafkaPublisher()
