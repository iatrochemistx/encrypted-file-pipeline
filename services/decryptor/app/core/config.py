import os
from functools import lru_cache

class Settings:
    kms_key_id: str = os.getenv(\"KMS_KEY_ID\", \"test-key-id\")

@lru_cache()
def get_settings():
    return Settings()
