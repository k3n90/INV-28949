# Тестовое задание от Invix (мой код INV-28949)

Каталог товаров: страница на Next.js, API на FastAPI, бот на aiogram 3. Фото хранятся в MinIO, записи о товарах — в PostgreSQL. Каталог открывается в браузере и в Telegram Mini App.

## Запуск

Нужны Docker и Docker Compose v2.

```bash
cp .env.example .env
docker compose up -d --build --scale web=2 --scale api=2 --scale bot=2
docker compose run --rm seed
```

Каталог: [http://localhost:8080](http://localhost:8080).

`seed` кладёт пять демо-товаров. Повторный запуск уже существующие имена пропускает.
Флаг `--scale <...>=2` нужен при каждом `up`, иначе сервисы `web`, `api` и `bot` вернутся к одному экземпляру. Это сделано для демонстрации того, что сервис живет в нескольких экземплярах сразу. Внутренний nginx сам находит все их адреса и распределяет запросы.

Webhook Telegram регистрируется сам, когда `PUBLIC_BASE_URL` начинается с `https://` (на локалке не сработает, нужно защищенное соединение).

## Параметры `.env`

Скопируйте `.env.example` в `.env` и заполните значения своими.
| Параметр | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram бота из @BotFather. |
| `ADMIN_IDS` | Числовые Telegram id администраторов через запятую. Админы могут добавлять товары. |
| `INTERNAL_TOKEN` | Общий секрет бота и API. Длинная случайная строка. |
| `WEBHOOK_SECRET` | Секрет webhook Telegram. Латиница, цифры, `_` и `-`. |
| `WEBAPP_URL` | Адрес кнопки «Открыть каталог». Локально `http://localhost:8080`, на стенде урла хоста `https://<SAMPLE_URL>.ru`. |
| `PUBLIC_BASE_URL` | Публичный адрес каталога. Из него собираются ссылки на картинки и URL webhook. |
| `POSTGRES_USER` | Пользователь PostgreSQL. В сэмпле — `INV-28949`. |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL. |
| `POSTGRES_DB` | Имя базы. В сэмпле — `shop`. |
| `MINIO_ROOT_USER` | Пользователь MinIO. В сэмпле — `INV-28949`. |
| `MINIO_ROOT_PASSWORD` | Пароль MinIO, от 8 символов. |
| `MINIO_BUCKET` | Бакет для фото. В сэмпле — `goods`. |
