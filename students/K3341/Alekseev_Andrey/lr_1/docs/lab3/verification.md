# Проверка и результаты

## Как запускался стек

```bash
cd students/K3341/Alekseev_Andrey/lr_3
cp .env.example .env
docker compose up --build -d
```

## Что проверялось

### 1. Поднятие контейнеров

Проверка:

```bash
docker compose ps
```

Фактическое состояние:

| Сервис | Статус |
| --- | --- |
| `lr3_finance_postgres` | `healthy` |
| `lr3_redis` | `healthy` |
| `lr3_parser_service` | `healthy` |
| `lr3_fastapi` | `healthy` |
| `lr3_celery_worker` | `up` |

### 2. Прямой вызов parser-service

Проверка:

```bash
POST http://127.0.0.1:8003/parse
```

Результат:

- `200 OK`
- `saved_count = 5`

### 3. Вызов через основной API

Проверка:

```bash
POST http://127.0.0.1:8002/api/v1/parser/parse
```

Результат:

- `200 OK`
- `saved_count = 5`

### 4. Вызов через Celery

Проверка:

```bash
POST http://127.0.0.1:8002/api/v1/parser/parse/queue
GET  http://127.0.0.1:8002/api/v1/parser/parse/queue/{task_id}
```

Результат:

- задача переходила `PENDING -> SUCCESS`
- итоговый ответ содержал `saved_count = 5`

## Проверка БД

Использовалась база:

```text
postgresql+psycopg2://finance_user:finance_pass@localhost:5433/finance_db_lr3
```

Проверочный запрос:

```sql
SELECT substring(description from 'Parser: ([^\n]+)') AS parser,
       count(*)
FROM transaction
WHERE description LIKE '%LR3 parser source:%'
GROUP BY 1
ORDER BY 1;
```

Фактический результат после прогонов:

| Parser | Rows |
| --- | ---: |
| `api-http` | 5 |
| `celery` | 5 |
| `direct-test` | 5 |

Итого:

- всего записей Lab 3: `15`

## Что пришлось исправить по ходу

Во время сборки и тестов были исправлены реальные сбои:

- parser-service сначала падал на конкурентных вставках в `user/tag/category`;
- проблема была устранена переводом вставок на `ON CONFLICT DO NOTHING`;
- после этого синхронный HTTP и Celery-сценарий отработали штатно.

## Вывод

Требования Lab 3 выполнены:

- FastAPI-приложение упаковано в Docker;
- parser-service упакован в Docker;
- общий стек поднимается через Docker Compose;
- парсер вызывается по HTTP из FastAPI;
- парсер вызывается через очередь Celery и Redis;
- данные реально сохраняются в PostgreSQL.
