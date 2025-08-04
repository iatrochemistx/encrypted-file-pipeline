from typing import Any, Dict, List, Optional
from app.messaging.event_publisher import AbstractEventPublisher

class InMemoryEventPublisher(AbstractEventPublisher):
    """
    In-memory event publisher stub for testing.
    Stores all published messages in an internal list.
    """
    
    def __init__(self):
        self.published_messages: List[Dict[str, Any]] = []
        self.published_routing_keys: List[str] = []
    
    async def publish(self, payload: Dict[str, Any], routing_key: Optional[str] = None) -> None:
        """
        Store the message in memory for test assertions.
        """
        self.published_messages.append(payload)
        self.published_routing_keys.append(routing_key or "file.decrypted")
    
    async def close(self) -> None:
        """
        No-op for in-memory publisher.
        """
        pass
    
    def get_published_messages(self) -> List[Dict[str, Any]]:
        """Get all published messages for assertions."""
        return self.published_messages.copy()
    
    def get_published_routing_keys(self) -> List[str]:
        """Get all published routing keys for assertions."""
        return self.published_routing_keys.copy()
    
    def clear(self) -> None:
        """Clear all stored messages for test isolation."""
        self.published_messages.clear()
        self.published_routing_keys.clear() 