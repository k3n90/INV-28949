import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/app")

from app.db import connect, insert_good
from app.s3 import ensure_bucket, put_object

GOODS = [
    ("Кружка", "mug.png"),
    ("Блокнот", "notebook.png"),
    ("Футболка", "tshirt.png"),
    ("Бутылка", "bottle.png"),
    ("Рюкзак", "backpack.png"),
]


def exists(name):
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM products WHERE name = %s",
            (name,),
        ).fetchone()
    return row is not None


def main():
    ensure_bucket()
    root = Path(__file__).resolve().parent / "images"
    for name, filename in GOODS:
        if exists(name):
            print("skip {0}".format(name))
            continue
        data = (root / filename).read_bytes()
        if filename.endswith(".png"):
            ext = "png"
            content_type = "image/png"
        else:
            ext = "jpg"
            content_type = "image/jpeg"
        key = "products/{0}.{1}".format(uuid.uuid4(), ext)
        put_object(key, data, content_type)
        insert_good(name, key)
        print("added {0}".format(name))


if __name__ == "__main__":
    main()
