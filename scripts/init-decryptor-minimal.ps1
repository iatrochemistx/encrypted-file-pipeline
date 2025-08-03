# init-decryptor-minimal.ps1

$svc = ".\services\decryptor"
$pkg = "$svc\app"

$dirs = @(
    "$pkg\api\v1",
    "$pkg\services",
    "$pkg\core",
    "$svc\tests"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    New-Item -ItemType File -Path (Join-Path $d "__init__.py") -Force | Out-Null
}

# main.py
@"
from fastapi import FastAPI
from .api.v1.decrypt import router as decrypt_router

def create_app():
    app = FastAPI(title=\"Decryptor Service\")
    app.include_router(decrypt_router, prefix=\"/v1\")
    return app

app = create_app()
"@ | Out-File "$pkg\main.py" -Encoding utf8

# decrypt route
@"
from fastapi import APIRouter, HTTPException
from ...services.decryptor import decrypt_file

router = APIRouter()

@router.post(\"/decrypt\")
async def decrypt_endpoint(payload: dict):
    file_id = payload.get(\"file_id\")
    if not file_id:
        raise HTTPException(status_code=400, detail=\"file_id required\")
    return decrypt_file(file_id)
"@ | Out-File "$pkg\api\v1\decrypt.py" -Encoding utf8

# business logic
@"
def decrypt_file(file_id: str) -> dict:
    # TODO: implement real decryption
    return {\"status\": \"ok\", \"file_id\": file_id}
"@ | Out-File "$pkg\services\decryptor.py" -Encoding utf8

# config loader
@"
import os
from functools import lru_cache

class Settings:
    kms_key_id: str = os.getenv(\"KMS_KEY_ID\", \"test-key-id\")

@lru_cache()
def get_settings():
    return Settings()
"@ | Out-File "$pkg\core\config.py" -Encoding utf8

# requirements
@"
fastapi
uvicorn[standard]
pydantic
"@ | Out-File "$svc\requirements.txt" -Encoding utf8

# Dockerfile
@"
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
"@ | Out-File "$svc\Dockerfile" -Encoding utf8

# .env.sample
@"
KMS_KEY_ID=test-key-id
"@ | Out-File "$svc\.env.sample" -Encoding utf8

Write-Host "`nScaffold created. Next steps:"
Write-Host "1. cd services\\decryptor"
Write-Host "2. python -m venv .venv"
Write-Host "3. .\\.venv\\Scripts\\Activate.ps1"
Write-Host "4. pip install -r requirements.txt"
Write-Host "5. uvicorn app.main:app --reload"
