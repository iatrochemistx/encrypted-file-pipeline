import os
import base64
from functools import lru_cache

class Settings:
    kms_key_id: str = os.getenv("KMS_KEY_ID", "test-key-id")
    data_dir: str = os.getenv("DATA_DIR", "/tmp/encrypted")
    
    @property
    def kms_data_key(self) -> bytes:
        """Get KMS data key, handling both plain text and base64 encoded keys."""
        key_value = os.getenv("KMS_DATA_KEY", "default-key")
        try:
            # Try to decode as base64 first
            return base64.b64decode(key_value)
        except Exception:
            # Fall back to plain text encoding
            return key_value.encode()

@lru_cache()
def get_settings():
    return Settings()
