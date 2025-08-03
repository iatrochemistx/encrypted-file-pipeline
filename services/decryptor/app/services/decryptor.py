"""Business-logic layer for the Decryptor service."""

from ..core.config import get_settings


def decrypt_file(file_id: str) -> dict:
    """
    Stub implementation.

    Eventually:
      • fetch encrypted object by `file_id`
      • decrypt with KMS-derived key
      • emit FileDecrypted event

    For now we just echo the ID so the HTTP stack and tests work.
    """
    settings = get_settings()       # proves DI/config wiring works
    _ = settings.kms_key_id         # not used yet, but accessed

    return {"status": "ok", "file_id": file_id}
