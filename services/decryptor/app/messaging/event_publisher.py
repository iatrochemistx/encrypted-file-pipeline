import json
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

import aio_pika
from aio_pika import Message, RobustConnection, DeliveryMode

class AbstractEventPublisher(ABC):
    @abstractmethod
    async def publish(self, payload: Dict[str, Any], routing_key: Optional[str] = None) -> None:
        pass
    @abstractmethod
    async def close(self) -> None:
        pass

class EventPublisher(AbstractEventPublisher):
    """
    Async, reusable RabbitMQ publisher with at-least-once delivery.
    """
    def __init__(self, amqp_url: str, default_routing_key: str = "file.decrypted") -> None:
        self._amqp_url = amqp_url
        self._default_routing_key = default_routing_key
        self._connection: Optional[RobustConnection] = None
        self._channel = None

    async def _ensure_connection(self) -> None:
        if self._connection and not self._connection.is_closed:
            return
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()

    async def publish(self, payload: Dict[str, Any], routing_key: Optional[str] = None) -> None:
        """
        Serialize and publish JSON payload.
        Raises on failure so callers can retry or report errors.
        """
        await self._ensure_connection()
        message = Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        actual_routing_key = routing_key or self._default_routing_key
        await self._channel.default_exchange.publish(
            message, routing_key=actual_routing_key
        )

    async def close(self) -> None:
        """
        Gracefully close the AMQP connection.
        """
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
