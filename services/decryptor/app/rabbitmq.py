import aio_pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

async def publish_file_decrypted(file_id: str, metadata: dict):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        message = aio_pika.Message(
            body=json.dumps({
                "file_id": file_id,
                "status": "decrypted",
                "metadata": metadata,
            }).encode()
        )
        await channel.default_exchange.publish(
            message,
            routing_key="file.decrypted"
        )
