# Тестовое задание от Invix (мой код INV-28949)

Демо-стенд: [https://invix.apostol-bot.ru](https://invix.apostol-bot.ru)
Демо-telegram: [https://t.me/INV28949_bot](https://t.me/INV28949_bot)


Каталог товаров: страница на Next.js, API на FastAPI, бот на aiogram 3. Фото хранятся в MinIO, записи о товарах — в PostgreSQL. Каталог открывается в браузере и в Telegram Mini App.

## Запуск

Нужны Docker и Docker Compose v2.

```bash
cp .env.example .env
docker compose up -d --build --scale web=2 --scale api=2 --scale bot=1
docker compose run --rm seed
```

Каталог: [http://localhost:8090](http://localhost:8090).

`seed` кладёт пять демо-товаров. Повторный запуск уже существующие имена пропускает.
Флаг `--scale <...>=2` нужен при каждом `up`, иначе сервисы `web` и `api` вернутся к одному экземпляру. Это сделано для демонстрации того, что сервис живет в нескольких экземплярах сразу. Внутренний nginx сам находит все их адреса и распределяет запросы.
upd. `bot` запускается в единственном экземпляре, т.к. при `BOT_MODE=polling` Telegram отдаёт очередь только одному получателю, второй получит ошибку Conflict. На зарубежном хосте можно запускать с параметром `--scale bot=2` при `BOT_MODE=webhook`.

Webhook Telegram регистрируется сам, когда `PUBLIC_BASE_URL` начинается с `https://` (на локалке не сработает, нужно защищенное соединение).

## Параметры `.env`

Скопируйте `.env.example` в `.env` и заполните значения своими.
| Параметр | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram бота из @BotFather. |
| `ADMIN_IDS` | Числовые Telegram id администраторов через запятую. Админы могут добавлять товары. |
| `INTERNAL_TOKEN` | Общий секрет бота и API. Длинная случайная строка. |
| `WEBHOOK_SECRET` | Секрет webhook Telegram. Латиница, цифры, `_` и `-`. |
| `TELEGRAM_PROXY` | Если сервак на РФ хосте. |
| `BOT_MODE` | Метод работы Telegram бота (polling/webhook). |
| `WEBAPP_URL` | Адрес кнопки «Открыть каталог» в Telegram боте. Локально `http://localhost:8090`, на демо-стенде урла хоста `https://<SAMPLE_URL>.ru`. |
| `PUBLIC_BASE_URL` | Публичный адрес каталога. Из него собираются ссылки на картинки и URL webhook. |
| `POSTGRES_USER` | Пользователь PostgreSQL. В сэмпле — `INV-28949`. |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL. |
| `POSTGRES_DB` | Имя базы. В сэмпле — `shop`. |
| `MINIO_ROOT_USER` | Пользователь MinIO. В сэмпле — `INV-28949`. |
| `MINIO_ROOT_PASSWORD` | Пароль MinIO, от 8 символов. |
| `MINIO_BUCKET` | Бакет для фото. В сэмпле — `goods`. |
