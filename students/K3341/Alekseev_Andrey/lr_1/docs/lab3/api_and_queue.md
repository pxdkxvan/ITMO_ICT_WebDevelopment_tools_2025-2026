# HTTP и очередь

## Прямой HTTP-вызов парсера

Маршрут в основном API:

```text
POST /api/v1/parser/parse
```

Файл:

- `lr_3/api_service/app/api/routes/parser.py`

Логика:

1. FastAPI принимает `url`;
2. основной API делает `POST` на `http://parser:8000/parse`;
3. parser-service выполняет парсинг и сохранение;
4. результат возвращается клиенту синхронно.

Пример:

```bash
curl -X POST http://localhost:8002/api/v1/parser/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://books.toscrape.com/catalogue/page-2.html"}'
```

Типичный успешный ответ:

```json
{
  "url": "https://books.toscrape.com/catalogue/page-2.html",
  "title": "All products | Books to Scrape - Sandbox",
  "parsed_by": "api-http",
  "extracted_count": 5,
  "saved_count": 5,
  "status": "ok"
}
```

## Асинхронный вызов через Celery

Маршрут постановки задачи:

```text
POST /api/v1/parser/parse/queue
```

Маршрут чтения результата:

```text
GET /api/v1/parser/parse/queue/{task_id}
```

Файлы:

- `lr_3/api_service/app/api/routes/parser.py`
- `lr_3/api_service/app/tasks.py`

### Что происходит

1. клиент вызывает `/parse/queue`;
2. основной API создает Celery-задачу `lr3.parse_url`;
3. задача попадает в Redis;
4. `celery_worker` забирает задачу;
5. worker вызывает `parser-service`;
6. результат возвращается в Redis backend;
7. клиент опрашивает `/parse/queue/{task_id}`.

Пример:

```bash
curl -X POST http://localhost:8002/api/v1/parser/parse/queue \
  -H "Content-Type: application/json" \
  -d '{"url":"https://books.toscrape.com/catalogue/page-3.html"}'
```

Ответ:

```json
{
  "task_id": "b51254f0-3a94-4039-879f-7b1cfbcb3af1",
  "status": "PENDING",
  "message": "Parsing task accepted"
}
```

Запрос результата:

```bash
curl http://localhost:8002/api/v1/parser/parse/queue/b51254f0-3a94-4039-879f-7b1cfbcb3af1
```

Успешный итог:

```json
{
  "task_id": "b51254f0-3a94-4039-879f-7b1cfbcb3af1",
  "status": "SUCCESS",
  "result": {
    "url": "https://books.toscrape.com/catalogue/page-3.html",
    "title": "All products | Books to Scrape - Sandbox",
    "parsed_by": "celery",
    "extracted_count": 5,
    "saved_count": 5,
    "status": "ok"
  }
}
```

## Почему здесь нужен Redis

Redis используется как:

- broker задач;
- backend результатов.

Без него Celery worker не сможет получать задачи от FastAPI и сохранять статусы `PENDING/SUCCESS/FAILURE`.

## Периодические задачи

В этой лабораторной периодические задачи не включались, но текущая структура уже готова к расширению:

- можно добавить Celery Beat;
- можно ставить регулярный парсинг заранее заданных URL;
- можно использовать ту же задачу `parse_url_task`.
