from fastapi import FastAPI
from .api.v1.decrypt import router as decrypt_router

def create_app():
    app = FastAPI(title=\"Decryptor Service\")
    app.include_router(decrypt_router, prefix=\"/v1\")
    return app

app = create_app()
