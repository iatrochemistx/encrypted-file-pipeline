# services/decryptor/app/services/decrypt_service.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import get_settings
from app.domain.repositories import FileRepository

class DecryptService:
    def __init__(self, file_repository: FileRepository):
        settings = get_settings()
        self.key = settings.kms_data_key
        self.file_repository = file_repository

    async def decrypt(self, file_id: str) -> bytes:
        """
        1) Load encrypted blob from repository
        2) Decrypt with AES-GCM using the provided key
        3) Return plaintext bytes
        """
        encrypted_data = await self.file_repository.read_encrypted(file_id)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, associated_data=None)
