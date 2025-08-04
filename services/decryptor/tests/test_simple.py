import os
import pytest
import asyncio
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.messaging.in_memory_event_publisher import InMemoryEventPublisher
from app.infrastructure.local_file_repository import LocalFileRepository
from app.services.decrypt_service import DecryptService

@pytest.mark.asyncio
async def test_in_memory_publisher():
    """Test that InMemoryEventPublisher works correctly."""
    publisher = InMemoryEventPublisher()
    
    # Test initial state
    assert len(publisher.get_published_messages()) == 0
    assert len(publisher.get_published_routing_keys()) == 0
    
    # Test publishing
    test_payload = {"file_id": "test", "status": "decrypted"}
    await publisher.publish(test_payload, "test.routing.key")
    
    # Check published messages
    messages = publisher.get_published_messages()
    routing_keys = publisher.get_published_routing_keys()
    
    assert len(messages) == 1
    assert len(routing_keys) == 1
    assert messages[0] == test_payload
    assert routing_keys[0] == "test.routing.key"
    
    # Test clear functionality
    publisher.clear()
    assert len(publisher.get_published_messages()) == 0
    assert len(publisher.get_published_routing_keys()) == 0

def test_file_repository_creation():
    """Test that LocalFileRepository can be created."""
    # Override data directory for testing
    original_data_dir = os.getenv("DATA_DIR")
    os.environ["DATA_DIR"] = "/tmp/test"
    
    try:
        repo = LocalFileRepository()
        assert repo is not None
        assert hasattr(repo, 'read_encrypted')
        assert callable(repo.read_encrypted)
    finally:
        if original_data_dir:
            os.environ["DATA_DIR"] = original_data_dir
        else:
            os.environ.pop("DATA_DIR", None)

def test_decrypt_service_creation():
    """Test that DecryptService can be created with dependencies."""
    # Override settings for testing
    original_kms_key = os.getenv("KMS_DATA_KEY")
    test_key = AESGCM.generate_key(bit_length=256)
    # Use base64 encoding for the key to avoid encoding issues
    import base64
    os.environ["KMS_DATA_KEY"] = base64.b64encode(test_key).decode()
    
    try:
        repo = LocalFileRepository()
        service = DecryptService(file_repository=repo)
        
        assert service is not None
        assert hasattr(service, 'decrypt')
        assert callable(service.decrypt)
        assert service.file_repository is repo
    finally:
        if original_kms_key:
            os.environ["KMS_DATA_KEY"] = original_kms_key
        else:
            os.environ.pop("KMS_DATA_KEY", None)

def test_imports_work():
    """Test that all imports work correctly."""
    try:
        from app.domain.repositories import FileRepository
        from app.infrastructure.local_file_repository import LocalFileRepository
        from app.services.decrypt_service import DecryptService
        from app.messaging.in_memory_event_publisher import InMemoryEventPublisher
        from app.main import create_app
        print("✅ All imports work correctly")
    except ImportError as e:
        pytest.fail(f"Import failed: {e}") 