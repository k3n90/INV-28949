import asyncio
import logging
import os
import re
import socket

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
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


def make_bot(token):
    proxy = os.environ.get("TELEGRAM_PROXY", "").strip() or None
    session = AiohttpSession(proxy=proxy, timeout=30)
    if proxy is None:
        session._connector_init["family"] = socket.AF_INET
    return Bot(token, session=session)


async def register_webhook(bot: Bot):
    try:
        addresses = sorted({item[4][0] for item in socket.getaddrinfo("api.telegram.org", 443)})
    except socket.gaierror as exc:
        addresses = ["dns error: {0}".format(exc)]
    log.info("api.telegram.org addresses: %s", ", ".join(addresses))
    base = settings.public_base_url
    if not base.startswith("https://"):
        log.info("webhook is not set, PUBLIC_BASE_URL=%s", base)
        return
    if not SECRET_RE.fullmatch(settings.webhook_secret):
        log.error("WEBHOOK_SECRET must match [A-Za-z0-9_-]{1,256}")
        return
    url = "{0}/telegram/webhook".format(base)
    attempt = 1
    while True:
        try:
            await bot.set_webhook(
                url=url,
                secret_token=settings.webhook_secret,
                allowed_updates=["message"],
                drop_pending_updates=False,
            )
        except Exception as exc:
            log.warning("set_webhook attempt %s failed: %s", attempt, exc)
            attempt += 1
            await asyncio.sleep(10)
            continue
        log.info("webhook set to %s", url)
        return


async def on_startup(bot: Bot):
    asyncio.create_task(register_webhook(bot))


async def run_polling(bot: Bot, dp: Dispatcher):
    await bot.delete_webhook(drop_pending_updates=False)
    log.info("webhook removed, receiving updates by polling")
    await dp.start_polling(bot, handle_signals=False, allowed_updates=["message"])


def main():
    app = web.Application()
    app.router.add_get("/health", health)

    if not TOKEN_RE.fullmatch(settings.bot_token):
        log.error("BOT_TOKEN is empty or not a Telegram token, webhook is off")
        web.run_app(app, host="0.0.0.0", port=8081)
        return

    bot = make_bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    if os.environ.get("BOT_MODE", "webhook").strip() == "polling":
        async def start_polling(_app):
            asyncio.create_task(run_polling(bot, dp))

        app.on_startup.append(start_polling)
        web.run_app(app, host="0.0.0.0", port=8081)
        return

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
