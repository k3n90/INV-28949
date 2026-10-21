import logging
import uuid

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from app.config import settings
from app.db import insert_good, list_goods
from app.s3 import put_object

log = logging.getLogger(__name__)
router = APIRouter()

IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_BYTES = 10 * 1024 * 1024


def to_item(row):
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "imageUrl": "{0}/media/{1}".format(settings.public_base_url, row["image_key"]),
        "created": row["created_at"].isoformat(),
    }


def looks_like_image(data, content_type):
    if content_type in ("image/jpeg", "image/jpg"):
        return data.startswith(b"\xff\xd8")
    if content_type == "image/png":
        return data.startswith(b"\x89PNG")
    if content_type == "image/webp":
        return len(data) >= 12 and data[8:12] == b"WEBP"
    return False


@router.get("/products")
def get_goods():
    return [to_item(row) for row in list_goods()]


@router.post("/products", status_code=201)
def create_good(
    name: str = Form(...),
    file: UploadFile = File(...),
    token: str = Header(default="", alias="X-Internal-Token"),
):
    expected = settings.internal_token
    if len(token) != len(expected) or token != expected:
        raise HTTPException(status_code=401, detail="unauthorized")

    title = name.strip()
    if not title or len(title) > 300:
        raise HTTPException(status_code=400, detail="bad name")

    content_type = (file.content_type or "").lower()
    ext = IMAGE_TYPES.get(content_type)
    data = file.file.read()
    if ext is None or not looks_like_image(data, content_type):
        raise HTTPException(status_code=400, detail="file must be an image")
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="bad file size")

    key = "products/{0}.{1}".format(uuid.uuid4(), ext)
    put_object(key, data, content_type)
    try:
        row = insert_good(title, key)
    except Exception:
        log.exception("product row was not saved, object %s left in the bucket", key)
        raise HTTPException(status_code=500, detail="could not save")
    return to_item(row)
