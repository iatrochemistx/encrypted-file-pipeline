import os
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi.testclient import TestClient
from app.main import create_app
from app.messaging.in_memory_event_publisher import InMemoryEventPublisher
from app.infrastructure.local_file_repository import LocalFileRepository
from app.services.decrypt_service import DecryptService

def create_encrypted_file(file_path: str, plaintext: bytes, key: bytes) -> None:
    """Helper function to create an encrypted file for testing."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    encrypted_data = nonce + ciphertext
    
    with open(file_path, "wb") as f:
        f.write(encrypted_data)

def test_decrypt_endpoint_integration(temp_data_dir):
    """
    Integration test that verifies the full request flow without external services.
    """
    # Arrange
    file_id = "test-integration-file"
    original_plaintext = b"This is a test message for API integration testing!"
    test_key = AESGCM.generate_key(bit_length=256)
    
    # Create encrypted file
    encrypted_file_path = temp_data_dir / f"{file_id}.enc"
    create_encrypted_file(str(encrypted_file_path), original_plaintext, test_key)
    
    # Create test dependencies
    in_memory_publisher = InMemoryEventPublisher()
    file_repository = LocalFileRepository(data_dir=str(temp_data_dir))
    
    # Override the KMS key for testing
    original_kms_key = os.getenv("KMS_DATA_KEY")
    import base64
    os.environ["KMS_DATA_KEY"] = base64.b64encode(test_key).decode()
    
    # Create decrypt service AFTER setting the environment variable
    decrypt_service = DecryptService(file_repository=file_repository)
    
    try:
        # Create FastAPI app with dependency overrides
        app = create_app()
        
        # Override dependencies for testing
        from app.deps import get_event_publisher, get_decrypt_service
        
        async def get_test_event_publisher():
            yield in_memory_publisher
        
        def get_test_decrypt_service():
            return decrypt_service
        
        app.dependency_overrides[get_event_publisher] = get_test_event_publisher
        app.dependency_overrides[get_decrypt_service] = get_test_decrypt_service
        
        # Create test client
        client = TestClient(app)
        
        # Act
        response = client.post(
            "/v1/decrypt",
            json={"file_id": file_id}
        )
        
        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Assert HTTP response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == {"status": "ok", "file_id": file_id}
        
        # Assert event publishing
        published_messages = in_memory_publisher.get_published_messages()
        published_routing_keys = in_memory_publisher.get_published_routing_keys()
        
        assert len(published_messages) == 1
        assert len(published_routing_keys) == 1
        
        # Check routing key
        assert published_routing_keys[0] == "file.decrypted"
        
        # Check payload content
        event_payload = published_messages[0]
        assert event_payload["file_id"] == file_id
        assert event_payload["byte_length"] == len(original_plaintext)
        assert event_payload["status"] == "decrypted"
        
    finally:
        # Restore original environment
        if original_kms_key:
            os.environ["KMS_DATA_KEY"] = original_kms_key
        else:
            os.environ.pop("KMS_DATA_KEY", None)

def test_decrypt_endpoint_file_not_found(temp_data_dir):
    """
    Test that missing files return 404.
    """
    # Arrange
    file_id = "non-existent-file"
    
    # Create test dependencies
    in_memory_publisher = InMemoryEventPublisher()
    file_repository = LocalFileRepository(data_dir=str(temp_data_dir))
    decrypt_service = DecryptService(file_repository=file_repository)
    
    try:
        # Create FastAPI app with dependency overrides
        app = create_app()
        
        # Override dependencies for testing
        from app.deps import get_event_publisher, get_decrypt_service
        
        async def get_test_event_publisher():
            yield in_memory_publisher
        
        def get_test_decrypt_service():
            return decrypt_service
        
        app.dependency_overrides[get_event_publisher] = get_test_event_publisher
        app.dependency_overrides[get_decrypt_service] = get_test_decrypt_service
        
        # Create test client
        client = TestClient(app)
        
        # Act
        response = client.post(
            "/v1/decrypt",
            json={"file_id": file_id}
        )
        
        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Assert HTTP response
        assert response.status_code == 404
        response_data = response.json()
        assert "not found" in response_data["detail"].lower()
        
        # Assert no events were published
        published_messages = in_memory_publisher.get_published_messages()
        assert len(published_messages) == 0
        
    finally:
        pass 