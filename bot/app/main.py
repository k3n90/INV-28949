import logging
import re

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import settings
from app.handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"^\d{8,10}:[A-Za-z0-9_-]{35}$")
SECRET_RE = re.compile(r"^[A-Za-z0-9_-]{1,256}$")


async def health(_request):
    return web.json_response({"status": "up"})


async def on_startup(bot: Bot):
    base = settings.public_base_url
    if not base.startswith("https://"):
        log.info("webhook is not set, PUBLIC_BASE_URL=%s", base)
        return
    if not SECRET_RE.fullmatch(settings.webhook_secret):
        raise RuntimeError("WEBHOOK_SECRET must match [A-Za-z0-9_-]{1,256}")
    await bot.set_webhook(
        url="{0}/telegram/webhook".format(base),
        secret_token=settings.webhook_secret,
        allowed_updates=["message"],
        drop_pending_updates=False,
    )
    log.info("webhook set to %s/telegram/webhook", base)


def main():
    app = web.Application()
    app.router.add_get("/health", health)

    if not TOKEN_RE.fullmatch(settings.bot_token):
        log.error("BOT_TOKEN is empty or not a Telegram token, webhook is off")
        web.run_app(app, host="0.0.0.0", port=8081)
        return

    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    ).register(app, path="/telegram/webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=8081)


if __name__ == "__main__":
    main()
