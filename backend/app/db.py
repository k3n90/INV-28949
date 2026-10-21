import logging
import time
import uuid

import psycopg
from psycopg.rows import dict_row

from app.config import settings

log = logging.getLogger(__name__)


def connect():
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def wait_db():
    last_error = None
    for _ in range(30):
        try:
            with connect() as conn:
                conn.execute("SELECT 1")
            return
        except Exception as exc:
            last_error = exc
            log.warning("postgres is not ready: %s", exc)
            time.sleep(2)
    raise RuntimeError("postgres is not ready: {0}".format(last_error))


def list_goods():
    # newest goods at the bottom of the catalog
    with connect() as conn:
        return conn.execute(
            """
            SELECT id, name, image_key, created_at
            FROM products
            ORDER BY created_at DESC
            """
        ).fetchall()


def insert_good(name, image_key):
    with connect() as conn:
        return conn.execute(
            """
            INSERT INTO products (id, name, image_key)
            VALUES (%s, %s, %s)
            RETURNING id, name, image_key, created_at
            """,
            (str(uuid.uuid4()), name, image_key),
        ).fetchone()
