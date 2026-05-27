# Архитектура и Docker

## Структура `lr_3`

```text
lr_3/
├── .env.example
├── docker-compose.yml
├── README.md
├── api_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── migrations/
│   └── app/
│       ├── api/routes/parser.py
│       ├── tasks.py
│       └── ...
└── parser_service/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── parser.py
        ├── storage.py
        └── config.py
```

## Сервисы в `docker-compose.yml`

### `postgres`

- образ: `postgres:18`
- хранит основную схему `lr_1`
- используется и основным API, и parser-service

### `redis`

- образ: `redis:7-alpine`
- работает как broker и result backend для Celery

### `parser`

- отдельный FastAPI-сервис
- принимает `POST /parse`
- загружает страницу, извлекает элементы и сохраняет их в БД

### `api`

- FastAPI-приложение на основе `lr_1`
- сохраняет все старые маршруты `auth`, `transactions`, `categories` и остальные
- получает новый роутер `/api/v1/parser/*`

### `celery_worker`

- поднимается на том же коде, что и `api_service`
- выполняет задачу `lr3.parse_url`
- вызывает `parser-service` в фоне

## Dockerfile

### `api_service/Dockerfile`

Использует `python:3.12-slim`, устанавливает зависимости, копирует код и запускает:

```bash
python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Это важно, потому что контейнер сам подготавливает схему БД перед стартом API.

### `parser_service/Dockerfile`

Тоже использует `python:3.12-slim`, но запускает только отдельное parser-приложение:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Почему parser-service выделен отдельно

Это выполняет требование лабораторной о внешнем вызове парсера по HTTP и одновременно разделяет ответственность:

- `api` занимается пользовательским API;
- `parser` занимается сетевым парсингом и сохранением результатов;
- `celery_worker` занимается асинхронным исполнением.

Такую структуру проще масштабировать и проверять по частям.

## Переменные окружения

Ключевые переменные:

- `DATABASE_URL`
- `PARSER_SERVICE_URL`
- `PARSER_REQUEST_TIMEOUT_SECONDS`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `APP_NAME`
- `APP_VERSION`
- `JWT_SECRET`
- `JWT_EXP_MINUTES`

Они передаются контейнерам через `docker-compose.yml`.
