from fastapi import APIRouter, HTTPException
from ...services.decryptor import decrypt_file

router = APIRouter()

@router.post(\"/decrypt\")
async def decrypt_endpoint(payload: dict):
    file_id = payload.get(\"file_id\")
    if not file_id:
        raise HTTPException(status_code=400, detail=\"file_id required\")
    return decrypt_file(file_id)
