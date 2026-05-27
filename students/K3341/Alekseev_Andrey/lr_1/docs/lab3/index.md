# Лабораторная работа 3

Lab 3 объединяет результаты первых двух лабораторных:

- основной FastAPI API из `lr_1`;
- парсер и логику сохранения из `lr_2`;
- контейнеризацию через Docker;
- синхронный HTTP-вызов парсера;
- асинхронный вызов парсера через Celery и Redis.

Исходный код находится в [students/K3341/Alekseev_Andrey/lr_3](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_3).

[Архитектура и Docker](architecture.md){ .md-button .md-button--primary }
[HTTP и очередь](api_and_queue.md){ .md-button .md-button--primary }
[Проверка и результаты](verification.md){ .md-button }

## Что реализовано

- отдельный контейнер `api` с FastAPI-приложением на базе `lr_1`;
- отдельный контейнер `parser` с FastAPI parser-service;
- отдельный контейнер `redis`;
- отдельный контейнер `celery_worker`;
- отдельный контейнер `postgres`;
- общий `docker-compose.yml`, который поднимает весь стек одной командой.

## Основные сценарии

### 1. Прямой вызов парсера по HTTP

Клиент вызывает основной API:

```text
POST /api/v1/parser/parse
```

Основной API отправляет внутренний HTTP-запрос в `parser-service`, а тот скачивает HTML, извлекает карточки и сохраняет их в PostgreSQL.

### 2. Асинхронный вызов через очередь

Клиент вызывает:

```text
POST /api/v1/parser/parse/queue
```

После этого:

1. задача попадает в Redis;
2. Celery worker забирает задачу;
3. worker вызывает `parser-service`;
4. результат доступен по `GET /api/v1/parser/parse/queue/{task_id}`.

## Источник данных

Для стабильной демонстрации используется:

- `https://books.toscrape.com/catalogue/page-1.html`
- `https://books.toscrape.com/catalogue/page-2.html`
- `https://books.toscrape.com/catalogue/page-3.html`

Парсер сохраняет первые 5 карточек со страницы.

## Порты

| Сервис | Порт |
| --- | ---: |
| `api` | `8002` |
| `parser` | `8003` |
| `postgres` | `5433` |
| `redis` | `6380` |
