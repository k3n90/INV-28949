import io
import json
import logging
import time

from minio import Minio

from app.config import settings

log = logging.getLogger(__name__)

client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)


def ensure_bucket():
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::{0}/*".format(settings.minio_bucket)],
            }
        ],
    }
    last_error = None
    for _ in range(30):
        try:
            if not client.bucket_exists(settings.minio_bucket):
                client.make_bucket(settings.minio_bucket)
            client.set_bucket_policy(settings.minio_bucket, json.dumps(policy))
            return
        except Exception as exc:
            last_error = exc
            log.warning("minio is not ready: %s", exc)
            time.sleep(2)
    raise RuntimeError("minio bucket was not created: {0}".format(last_error))


def put_object(key, data, content_type):
    client.put_object(
        settings.minio_bucket,
        key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
