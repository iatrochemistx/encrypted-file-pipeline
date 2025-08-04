from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.v1.decrypt import router as decrypt_router
from .deps import get_publisher_singleton

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    publisher = get_publisher_singleton()
    await publisher.close()

def create_app():
    app = FastAPI(title="Decryptor Service", lifespan=lifespan)
    app.include_router(decrypt_router, prefix="/v1")
    return app

app = create_app()
