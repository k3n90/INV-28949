import io
import logging

import httpx
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

from app.config import settings

log = logging.getLogger(__name__)
router = Router()

MAX_BYTES = 10 * 1024 * 1024


def is_admin(message):
    user = message.from_user
    return user is not None and user.id in settings.admin_ids


def menu(message):
    rows = [
        [
            KeyboardButton(
                text="Открыть каталог",
                web_app=WebAppInfo(url=settings.webapp_url),
            )
        ]
    ]
    if is_admin(message):
        rows.append([KeyboardButton(text="Создать товар")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


@router.message(CommandStart())
async def on_start(message: Message):
    await message.answer("У меня есть товар", reply_markup=menu(message))


@router.message(F.text == "Создать товар")
async def on_create_good(message: Message):
    if not is_admin(message):
        await message.answer("У меня есть товар", reply_markup=menu(message))
        return
    await message.answer(
        "Отправьте одно сообщение: фотография через скрепку и название в подписи.",
        reply_markup=menu(message),
    )


@router.message(F.photo)
async def on_photo(message: Message, bot: Bot):
    if not is_admin(message):
        await message.answer(
            "Добавлять товары может только администратор.",
            reply_markup=menu(message),
        )
        return

    title = (message.caption or "").strip()
    if not title:
        await message.answer(
            "Пришлите фото через скрепку и название одним сообщением: название — в подписи к фото."
        )
        return

    photo = message.photo[-1]
    if photo.file_size and photo.file_size > MAX_BYTES:
        await message.answer("Файл больше 10 МБ.")
        return

    buffer = io.BytesIO()
    await bot.download(photo, destination=buffer)
    payload = buffer.getvalue()
    if not payload or len(payload) > MAX_BYTES:
        await message.answer("Файл больше 10 МБ.")
        return

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "{0}/api/products".format(settings.api_url),
                headers={"X-Internal-Token": settings.internal_token},
                data={"name": title},
                files={"file": ("photo.jpg", payload, "image/jpeg")},
            )
    except httpx.HTTPError:
        log.exception("api request failed")
        await message.answer("Не получилось сохранить товар.")
        return

    if response.status_code >= 400:
        log.warning("api rejected product: %s %s", response.status_code, response.text)
        await message.answer("Не получилось сохранить товар.")
        return

    await message.answer("Товар «{0}» добавлен.".format(title))


@router.message(F.text)
async def on_text(message: Message):
    await message.answer("Каталог товаров", reply_markup=menu(message))
