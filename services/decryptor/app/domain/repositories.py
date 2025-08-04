from abc import ABC, abstractmethod
from typing import Protocol

class FileRepository(Protocol):
    """Abstract interface for file repository operations."""
    
    @abstractmethod
    async def read_encrypted(self, file_id: str) -> bytes:
        """
        Read encrypted file data asynchronously.
        
        Args:
            file_id: The identifier of the file to read
            
        Returns:
            The encrypted file data as bytes
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        pass 