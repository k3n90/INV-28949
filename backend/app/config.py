import os
from dataclasses import dataclass


def _endpoint(value):
    text = value.strip()
    if text.startswith("https://"):
        text = text[len("https://"):]
    if text.startswith("http://"):
        text = text[len("http://"):]
    return text.strip("/")


@dataclass(frozen=True)
class Settings:
    database_url: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    internal_token: str
    public_base_url: str


def load():
    user = os.environ.get("POSTGRES_USER", "")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    database = os.environ.get("POSTGRES_DB", "")
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = os.environ.get("POSTGRES_PORT", "5432")
    database_url = os.environ.get("DATABASE_URL") or (
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )
    )
    public = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8080").rstrip("/")
    return Settings(
        database_url=database_url,
        minio_endpoint=_endpoint(os.environ.get("MINIO_ENDPOINT", "minio:9000")),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY", ""),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY", ""),
        minio_bucket=os.environ.get("MINIO_BUCKET", ""),
        internal_token=os.environ.get("INTERNAL_TOKEN", ""),
        public_base_url=public,
    )


settings = load()
