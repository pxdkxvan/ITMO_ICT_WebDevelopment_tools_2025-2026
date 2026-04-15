# Практическая навигация по проекту

Этот файл отвечает на вопрос "куда идти и что менять" для типовых задач разработчика.

## Если нужно изменить или добавить эндпоинт

1. Открой нужный роутер в `app/api/routes/`:
   - auth: `auth.py`
   - users: `users.py`
   - categories: `categories.py`
   - tags: `tags.py`
   - transactions: `transactions.py`
   - budgets: `budgets.py`
   - goals: `goals.py`
   - reports: `reports.py`
2. Добавь/измени функцию с декоратором `@router.<method>(...)`.
3. Если нужен новый формат запроса/ответа, добавь схему в `app/schemas/<domain>.py`.
4. Если нужен JWT-доступ, добавь `current_user: CurrentUserDep` в сигнатуру.
5. Если нужен доступ к БД, добавь `session: SessionDep`.
6. Убедись, что роутер подключен в `app/api/__init__.py`.

## Если нужно изменить бизнес-логику

Сейчас логика находится в самих роутерах, поэтому меняется прямо там:

- правила владения сущностями (`user_id` проверки) — в CRUD-функциях роутеров;
- формирование вложенных DTO — helpers `_build_transaction_read`, `_budget_read`;
- вычисления отчетов — `reports.py`.

Если логика растет, рекомендуемый рефакторинг:

1. создать `app/services/`;
2. вынести доменные функции из роутеров в сервисы;
3. оставить в роутерах только парсинг HTTP, вызов сервиса и возврат response model.

## Если нужно изменить структуру БД

1. Правка модели: `app/models/entities.py`.
2. Создание миграции Alembic (новой ревизии) в `migrations/versions/`.
3. Применение: `alembic upgrade head`.
4. Обновление схем API (если изменился контракт): `app/schemas/*`.
5. Обновление роутеров под новые поля/связи.

Важно: не редактируй старую миграцию `0001` в общем случае для shared-окружений; добавляй новую миграцию поверх.

## Если нужно изменить JWT/пароли

- `app/core/security.py`
  - `hash_password`, `verify_password`
  - `create_access_token`, `decode_access_token`
- `app/core/config.py`
  - `JWT_SECRET`, `JWT_EXP_MINUTES`, `jwt_algorithm`

При изменении формата токена убедись, что `app/api/deps.py::get_current_user` все еще извлекает `sub` и корректно маппит в `User.id`.

## Если нужно поменять окружение и подключение к БД

- `.env` — значения переменных.
- `app/core/config.py` — обязательность/env-ключи.
- `app/db/session.py` — создание SQLAlchemy engine.
- `docker-compose.yml` — локальный PostgreSQL.
- `migrations/env.py` и `alembic.ini` — интеграция Alembic.

## Быстрый чеклист при внесении изменений

1. Обновить схемы (`app/schemas`) и роуты (`app/api/routes`) синхронно.
2. Для новых полей в БД — миграция обязательна.
3. Проверить документацию Swagger (`/docs`).
4. Проверить миграции на чистой БД (`docker compose down -v && up -d`, затем `alembic upgrade head`).
5. Проверить авторизацию на защищенных ручках (401/200).
