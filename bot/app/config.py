import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: frozenset
    internal_token: str
    api_url: str
    webapp_url: str
    public_base_url: str
    webhook_secret: str


def load():
    ids = set()
    raw = os.environ.get("ADMIN_IDS", "")
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        ids.add(int(part))
    return Settings(
        bot_token=os.environ.get("BOT_TOKEN", "").strip(),
        admin_ids=frozenset(ids),
        internal_token=os.environ.get("INTERNAL_TOKEN", ""),
        api_url=os.environ.get("API_URL", "").rstrip("/"),
        webapp_url=os.environ.get("WEBAPP_URL", "http://localhost:8080").rstrip("/"),
        public_base_url=os.environ.get("PUBLIC_BASE_URL", "http://localhost:8080").rstrip("/"),
        webhook_secret=os.environ.get("WEBHOOK_SECRET", ""),
    )


settings = load()
