import os
import tempfile
import pytest
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.infrastructure.local_file_repository import LocalFileRepository
from app.services.decrypt_service import DecryptService

@pytest.fixture
def test_data_dir():
    """Create a dedicated test data directory."""
    # Create a test data directory in the project root
    test_dir = Path(__file__).parent.parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def test_key():
    """Generate a test AES-GCM key."""
    return AESGCM.generate_key(bit_length=256)

@pytest.fixture
def file_repository(temp_data_dir):
    """Create a LocalFileRepository with explicit temp directory."""
    repo = LocalFileRepository(data_dir=str(temp_data_dir))
    return repo

@pytest.fixture
def decrypt_service(file_repository, test_key):
    """Create a DecryptService with test key and repository."""
    # Override the KMS data key for testing
    original_key = os.getenv("KMS_DATA_KEY")
    import base64
    os.environ["KMS_DATA_KEY"] = base64.b64encode(test_key).decode()
    
    try:
        service = DecryptService(file_repository=file_repository)
        yield service
    finally:
        # Restore original environment
        if original_key:
            os.environ["KMS_DATA_KEY"] = original_key
        else:
            os.environ.pop("KMS_DATA_KEY", None)

def create_encrypted_file(file_path: str, plaintext: bytes, key: bytes) -> None:
    """Helper function to create an encrypted file for testing."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    encrypted_data = nonce + ciphertext
    
    with open(file_path, "wb") as f:
        f.write(encrypted_data) 