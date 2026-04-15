# Бизнес-логика и цепочки вызовов

В текущем проекте отдельного service-слоя нет. Поэтому фактическая цепочка выглядит так:

`endpoint (app/api/routes/*.py) -> helper-функции (локальные) -> SQLModel Session -> PostgreSQL`.

Это важное архитектурное наблюдение: если в задаче ожидается явный слой `services`, сейчас его роль выполняют функции роутеров.

## Где находится логика

- Авторизация и криптография: `app/core/security.py`
- Доступ к текущему пользователю (auth gate): `app/api/deps.py::get_current_user`
- Доменные операции CRUD: `app/api/routes/*.py`
- ORM-модели и связи: `app/models/entities.py`
- Валидация payload/response: `app/schemas/*.py`

## Цепочка вызовов (на примерах)

### 1) Регистрация пользователя

1. Клиент вызывает `POST /api/v1/auth/register`.
2. `auth.py::register(payload, session)` валидирует body через `RegisterRequest`.
3. Через `session.exec(select(User).where(User.email == payload.email)).first()` проверяется уникальность email.
4. Пароль хэшируется `security.py::hash_password`.
5. Создается `User(...)`, затем `session.add -> commit -> refresh`.
6. Возврат в `response_model=UserRead`.

### 2) Вход и получение JWT

1. `POST /api/v1/auth/login` с email+password.
2. `auth.py::login` читает пользователя из БД.
3. Пароль проверяется `verify_password`.
4. Создается токен `create_access_token(str(user.id))`.
5. Возвращается `TokenResponse`.

### 3) Создание транзакции и вложенный ответ

1. `POST /api/v1/transactions`.
2. `transactions.py::create_transaction` получает `CurrentUserDep` и `SessionDep`.
3. Проверка категории: `session.get(Category, payload.category_id)` + сверка `category.user_id == current_user.id`.
4. Создание `Transaction(...)`, сохранение (`add/commit/refresh`).
5. Построение вложенного ответа через `_build_transaction_read(tx, session)`:
   - подгрузка категории;
   - выборка link-таблицы `TransactionTagLink`;
   - подгрузка тегов и сборка `TransactionTagRead`.
6. Клиент получает `TransactionRead` с вложенными объектами.

### 4) Привязка тега к транзакции (many-to-many + атрибут связи)

1. `POST /api/v1/transactions/{transaction_id}/tags`.
2. Проверяется существование и ownership транзакции/тега.
3. `session.get(TransactionTagLink, (transaction_id, payload.tag_id))`:
   - если link найден, обновляются `importance` и `note`;
   - иначе создается новый `TransactionTagLink`.
4. `session.add(link)` и `commit`.
5. Возвращается обновленный `TransactionRead`.

### 5) Отчет по месяцу

1. `GET /api/v1/reports/summary?month=YYYY-MM`.
2. `reports.py::monthly_summary` вычисляет `date`-границы через `_month_start/_next_month`.
3. SQLModel `select(Transaction).where(...)` получает транзакции пользователя в диапазоне дат.
4. Python-агрегация считает итоги доходов/расходов и map расходов по категориям.
5. Возвращается `MonthlySummaryRead`.

## SQL/ORM паттерны, которые используются в проекте

- выборка списка: `session.exec(select(Model).where(...)).all()`;
- выборка одиночной сущности по PK: `session.get(Model, id)`;
- создание: `session.add(...)`, `commit`, `refresh`;
- обновление: `payload.model_dump(exclude_unset=True)` + `setattr(...)` + `commit`;
- удаление: `session.delete(...)`, `commit`.

Прямых SQL-строк нет, кроме DDL в Alembic-миграции.

## Предположения и неочевидные моменты

- Предположение: проект ориентирован на single-process API без фоновых воркеров; это следует из отсутствия очередей/tasks.
- Неочевидность: `reports` не валидирует формат `month` на уровне схемы, поэтому некорректные значения могут приводить к `500`.
- Неочевидность: удаление `Category`/`Tag`/`Budget` опирается на дефолтное поведение FK в PostgreSQL и SQLModel без явного `cascade` в моделях.
