import asyncio
import json
from collections.abc import Awaitable, Callable

from aiokafka import AIOKafkaConsumer

from app.core.config import settings
from app.platform.events import TOPICS
from app.platform.messaging import kafka_publisher

Handler = Callable[[dict], Awaitable[None]]


class ReliableConsumer:
    def __init__(self, topic: str, group_id: str, handler: Handler, retries: int = 3):
        self.topic = topic
        self.group_id = group_id
        self.handler = handler
        self.retries = retries
        self.consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            enable_auto_commit=False,
        )
        await self.consumer.start()

    async def stop(self) -> None:
        if self.consumer:
            await self.consumer.stop()

    async def run_forever(self) -> None:
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        async for message in self.consumer:
            payload = message.value
            success = False
            for attempt in range(1, self.retries + 1):
                try:
                    await self.handler(payload)
                    success = True
                    break
                except Exception:
                    await asyncio.sleep(attempt)

            if not success:
                dlq_topic = TOPICS[self.topic].dlq if self.topic in TOPICS else f"{self.topic}.dlq"
                await kafka_publisher.publish(dlq_topic, payload)

            await self.consumer.commit()
