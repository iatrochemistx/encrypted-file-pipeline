import pytest
from app.services.decrypt_service import DecryptService
from app.infrastructure.local_file_repository import LocalFileRepository

def test_decrypt_service_initialization():
    """Test that DecryptService can be initialized with a file repository."""
    file_repository = LocalFileRepository()
    decrypt_service = DecryptService(file_repository=file_repository)
    assert decrypt_service is not None
    assert decrypt_service.file_repository is file_repository

def test_decrypt_service_has_decrypt_method():
    """Test that the decrypt method exists and is callable."""
    file_repository = LocalFileRepository()
    decrypt_service = DecryptService(file_repository=file_repository)
    
    # Test that the method exists and is callable
    assert hasattr(decrypt_service, 'decrypt')
    assert callable(decrypt_service.decrypt)
