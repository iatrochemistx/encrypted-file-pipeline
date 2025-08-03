# app/api/v1/decrypt.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.rabbitmq import publish_file_decrypted

router = APIRouter()

class DecryptRequest(BaseModel):
    file_id: str

@router.post("/decrypt")
async def decrypt_file(req: DecryptRequest):
    await publish_file_decrypted(req.file_id, metadata={})
    return {"status": "ok", "file_id": req.file_id}
