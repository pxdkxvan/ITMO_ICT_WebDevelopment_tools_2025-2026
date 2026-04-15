# Practice 1.3

Выполнено в основном проекте:

- Alembic (`alembic.ini`, `migrations/`, `migrations/versions/0001_init_finance_schema.py`)
- `.env` через `python-dotenv` (см. `app/core/config.py` и `migrations/env.py`)
- `.gitignore` с исключением `*.env`
- Структура проекта с разделением по слоям: `api`, `models`, `schemas`, `db`, `core`

Команды:

```bash
alembic upgrade head
uvicorn main:app --reload
```
