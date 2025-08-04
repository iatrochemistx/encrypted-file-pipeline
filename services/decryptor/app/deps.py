import os
from functools import lru_cache
from typing import AsyncGenerator

from app.messaging.event_publisher import EventPublisher, AbstractEventPublisher
from app.infrastructure.local_file_repository import LocalFileRepository
from app.services.decrypt_service import DecryptService
from app.domain.repositories import FileRepository

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

@lru_cache()
def get_publisher_singleton() -> AbstractEventPublisher:
    """
    Single, cached EventPublisher instance for the app's lifetime.
    """
    return EventPublisher(amqp_url=RABBITMQ_URL)

async def get_event_publisher() -> AsyncGenerator[AbstractEventPublisher, None]:
    """
    FastAPI dependency: yields the shared publisher.
    """
    publisher = get_publisher_singleton()
    yield publisher
    # Do *not* close here; we'll handle shutdown centrally.

def get_file_repository() -> FileRepository:
    """
    FastAPI dependency: returns the file repository singleton.
    """
    return LocalFileRepository()

def get_decrypt_service() -> DecryptService:
    """
    FastAPI dependency: returns the decrypt service with injected dependencies.
    """
    file_repository = get_file_repository()
    return DecryptService(file_repository=file_repository)
