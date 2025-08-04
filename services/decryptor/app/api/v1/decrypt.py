from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.deps import get_event_publisher, get_decrypt_service
from app.messaging.event_publisher import AbstractEventPublisher
from app.services.decrypt_service import DecryptService

router = APIRouter()

class DecryptRequest(BaseModel):
    file_id: str

@router.post("/decrypt")
async def decrypt_file(
    req: DecryptRequest,
    publisher: AbstractEventPublisher = Depends(get_event_publisher),
    decrypt_service: DecryptService = Depends(get_decrypt_service),
):
    try:
        plaintext = await decrypt_service.decrypt(req.file_id)
        
        # Publish event with file_id and byte length
        event_payload = {
            "file_id": req.file_id, 
            "byte_length": len(plaintext),
            "status": "decrypted"
        }
        await publisher.publish(event_payload, routing_key="file.decrypted")
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as-is
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to decrypt or publish event") from exc

    return {"status": "ok", "file_id": req.file_id}
