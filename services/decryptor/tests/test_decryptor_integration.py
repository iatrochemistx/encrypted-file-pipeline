import pytest
from app.infrastructure.local_file_repository import LocalFileRepository
from app.services.decrypt_service import DecryptService
from .conftest import create_encrypted_file

@pytest.mark.asyncio
async def test_round_trip_encrypt_decrypt(file_repository, decrypt_service, test_key, temp_data_dir):
    """Test the complete encrypt→decrypt round-trip with LocalFileRepository."""
    
    # Test data
    file_id = "test-file-123"
    original_plaintext = b"Hello, this is a test message for encryption and decryption!"
    
    # Create encrypted file
    file_path = temp_data_dir / f"{file_id}.enc"
    create_encrypted_file(str(file_path), original_plaintext, test_key)
    
    # Verify file exists
    assert file_path.exists()
    
    # Decrypt the file
    decrypted_plaintext = await decrypt_service.decrypt(file_id)
    
    # Verify the decrypted content matches the original
    assert decrypted_plaintext == original_plaintext
    assert len(decrypted_plaintext) == len(original_plaintext)

@pytest.mark.asyncio
async def test_file_not_found(file_repository, decrypt_service):
    """Test that missing files return 404."""
    
    with pytest.raises(Exception) as exc_info:
        await decrypt_service.decrypt("non-existent-file")
    
    # The exception should be an HTTPException with 404 status
    assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_repository_read_encrypted(file_repository, temp_data_dir, test_key):
    """Test the repository's read_encrypted method directly."""
    
    file_id = "direct-test-file"
    test_data = b"Direct repository test data"
    
    # Create encrypted file
    file_path = temp_data_dir / f"{file_id}.enc"
    create_encrypted_file(str(file_path), test_data, test_key)
    
    # Read encrypted data
    encrypted_data = await file_repository.read_encrypted(file_id)
    
    # Verify we got some data (the encrypted bytes)
    assert len(encrypted_data) > 0
    assert encrypted_data != test_data  # Should be encrypted, not plaintext 