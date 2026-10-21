import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import wait_db
from app.routers.products import router
from app.s3 import ensure_bucket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(_app):
    if len(settings.internal_token) < 8:
        raise RuntimeError("INTERNAL_TOKEN must be 8+ characters")
    wait_db()
    ensure_bucket()
    yield


app = FastAPI(title="invix", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "up"}
