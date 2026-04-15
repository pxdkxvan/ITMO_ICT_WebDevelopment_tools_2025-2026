# Архитектура приложения

Приложение построено как монолитный HTTP API на FastAPI с SQLModel (поверх SQLAlchemy) и PostgreSQL. Архитектурно код разделен на пять слоев: вход API (`app/main.py`, `app/api/*`), зависимости/авторизация (`app/api/deps.py`), схемы сериализации (`app/schemas/*`), доменные ORM-модели (`app/models/entities.py`), инфраструктура (`app/core/*`, `app/db/session.py`, `migrations/*`).

Точка старта HTTP-приложения — функция создания `FastAPI`-объекта в `app/main.py`:

- `app = FastAPI(title=settings.app_name, version=settings.app_version)`
- `app.include_router(api_router)`
- `root()` на `GET /`

Файл `main.py` в корне — thin entrypoint, просто экспортирует объект `app` из `app.main`.

Маршруты агрегируются в `app/api/__init__.py`: там создается `APIRouter(prefix="/api/v1")`, и в него подключаются все роутеры (`auth`, `users`, `categories`, `tags`, `transactions`, `budgets`, `goals`, `reports`).

Конфигурация поднимается из `.env` через `python-dotenv` в `app/core/config.py`. Класс `Settings` объявлен как `dataclass(frozen=True)` и использует `_require_env(...)`, поэтому ключевые переменные обязательны (`APP_NAME`, `APP_VERSION`, `DATABASE_URL`, `JWT_SECRET`, `JWT_EXP_MINUTES`). Если переменной нет, приложение падает на старте `RuntimeError`.

Слой безопасности расположен в `app/core/security.py`. Здесь вручную реализованы:

- хэширование пароля (`hash_password`) через `PBKDF2-HMAC-SHA256` + salt;
- проверка пароля (`verify_password`) через `hmac.compare_digest`;
- выпуск JWT (`create_access_token`) как компактной JWS-строки с HMAC-SHA256;
- валидация JWT (`decode_access_token`) с проверкой подписи и `exp`.

Взаимодействие с БД сосредоточено в `app/db/session.py`:

- `engine = create_engine(settings.database_url, echo=False)`;
- `get_session()` выдает SQLModel `Session` через dependency-injection;
- `init_db()` существует, но в основном потоке используется Alembic-миграция, а не `create_all`.

Модели данных (таблицы и связи) описаны в `app/models/entities.py`. Там определены `User`, `Category`, `Transaction`, `Tag`, `TransactionTagLink`, `Budget`, `Goal`, а также enum-типы Python (`TransactionKind`, `GoalStatus`) для API-валидации. Важно: в БД значения `kind`/`status` хранятся как `VARCHAR` (после последних изменений миграции), а enum-контроль делается уровнем Pydantic-схем.

Схемы API находятся в `app/schemas/*`:

- запросы/ответы auth: `auth.py`, `users.py`;
- CRUD-схемы доменных сущностей: `categories.py`, `tags.py`, `transactions.py`, `budgets.py`, `goals.py`;
- отчеты: `reports.py`.

## Поток запроса от HTTP до ответа

Ниже фактический поток выполнения для большинства защищенных ручек:

1. HTTP запрос приходит в endpoint-функцию из файла `app/api/routes/*.py`.
2. FastAPI собирает зависимости (`Depends`):
   - `SessionDep` из `app/api/deps.py` -> `get_session()` из `app/db/session.py`;
   - `CurrentUserDep` из `app/api/deps.py` -> `get_current_user()`.
3. В `get_current_user()` токен извлекается через `HTTPBearer`, декодируется `decode_access_token()`, из payload берется `sub`, затем читается `User` из БД (`select(User).where(User.id == user_id)`).
4. Endpoint валидирует входные данные через Pydantic-схемы (`payload`), применяет бизнес-правила (например, проверка владения сущностью по `user_id`), затем выполняет SQLModel операции:
   - `session.get(...)`
   - `session.exec(select(...).where(...))`
   - `session.add(...)`
   - `session.delete(...)`
   - `session.commit()`
   - `session.refresh(...)`
5. Возвращаемый Python-объект сериализуется в `response_model` (если указан), и клиент получает JSON.

## Наблюдение по архитектуре сервисного слоя

Сервисного слоя в отдельной директории (`services/`) сейчас нет. Бизнес-логика распределена напрямую по endpoint-функциям роутеров, а повторяющиеся фрагменты вынесены в приватные helper-функции внутри роутеров:

- `_build_transaction_read(...)` в `app/api/routes/transactions.py`;
- `_budget_read(...)` в `app/api/routes/budgets.py`;
- `_month_start(...)`, `_next_month(...)` в `app/api/routes/reports.py`.

Это рабочая схема для небольшого проекта, но при росте функциональности стоит вынести бизнес-операции в отдельный слой сервисов и оставить в роутерах только HTTP-адаптацию.
