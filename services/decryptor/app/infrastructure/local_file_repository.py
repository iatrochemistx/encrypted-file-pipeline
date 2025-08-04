import os
import aiofiles
from pathlib import Path
from fastapi import HTTPException
from app.domain.repositories import FileRepository
from app.core.config import get_settings

class LocalFileRepository(FileRepository):
    """Local file system implementation of FileRepository using aiofiles."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            settings = get_settings()
            self.data_dir = Path(settings.data_dir)
        else:
            self.data_dir = Path(data_dir)
        
        # Ensure data directory exists with proper path handling
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def read_encrypted(self, file_id: str) -> bytes:
        """
        Read encrypted file data asynchronously from local filesystem.
        
        Args:
            file_id: The identifier of the file to read
            
        Returns:
            The encrypted file data as bytes
            
        Raises:
            HTTPException: 404 if file not found
        """
        file_path = self.data_dir / f"{file_id}.enc"
        
        try:
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()
        except FileNotFoundError:
            raise HTTPException(
                status_code=404, 
                detail=f"Encrypted file not found: {file_id}"
            ) 