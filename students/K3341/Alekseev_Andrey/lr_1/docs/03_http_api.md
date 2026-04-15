# HTTP API: полный каталог ручек

Базовый префикс API: `/api/v1` (см. `app/api/__init__.py`).

Авторизация для защищенных ручек: заголовок

```http
Authorization: Bearer <access_token>
```

Получение токена: `POST /api/v1/auth/login`.

Во всех ручках с body возможна стандартная ошибка FastAPI `422 Unprocessable Entity` при невалидном JSON/типах/ограничениях схем.

## 0) Системная ручка

### `GET /`

- Код: `app/main.py`, функция `root`.
- Назначение: health-check приложения.
- Параметры: нет.
- Ответ `200`:

```json
{"message": "Personal Finance API is running"}
```

## 1) Auth (`app/api/routes/auth.py`)

### `POST /api/v1/auth/register`

- Функция: `register`.
- Body (`RegisterRequest`): `email`, `full_name`, `password`.
- Действие: проверяет уникальность email, хэширует пароль, создает `User`.
- Ответ `201` (`UserRead`):

```json
{
  "id": 1,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2026-04-15T15:00:00"
}
```

- Ошибки:
  - `409 Email already exists`.
  - `422` валидация (например, короткий пароль).

### `POST /api/v1/auth/login`

- Функция: `login`.
- Body (`LoginRequest`): `email`, `password`.
- Действие: проверяет пароль, выдает JWT.
- Ответ `200` (`TokenResponse`):

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

- Ошибки:
  - `401 Invalid credentials`.
  - `422`.

### `GET /api/v1/auth/me`

- Функция: `me`.
- Требует `CurrentUserDep` (JWT).
- Ответ `200` (`UserRead`) — текущий пользователь.
- Ошибки:
  - `401 Missing token`.
  - `401 Invalid token|Invalid token signature|Token expired|User not found`.

### `PATCH /api/v1/auth/me/password`

- Функция: `change_password`.
- Требует JWT.
- Body (`ChangePasswordRequest`): `old_password`, `new_password`.
- Действие: проверяет старый пароль, перехэширует новый.
- Ответ `204` без тела.
- Ошибки:
  - `401 Old password is incorrect`.
  - `401` ошибки токена.
  - `422`.

## 2) Users (`app/api/routes/users.py`)

### `GET /api/v1/users`

- Функция: `users_list`.
- Требует JWT.
- Назначение: список пользователей в публичном виде.
- Ответ `200` (`list[UserPublicRead]`):

```json
[
  {"id": 1, "email": "a@example.com", "full_name": "A"},
  {"id": 2, "email": "b@example.com", "full_name": "B"}
]
```

- Ошибки: `401` токен.

## 3) Categories (`app/api/routes/categories.py`)

### `GET /api/v1/categories`

- Функция: `list_categories`.
- Требует JWT.
- Возвращает только категории текущего пользователя.
- Ответ `200` (`list[CategoryRead]`).

### `POST /api/v1/categories`

- Функция: `create_category`.
- Body (`CategoryCreate`):

```json
{"name": "Food", "kind": "expense"}
```

- Ответ `201` (`CategoryRead`).
- Ошибки: `401`, `422`.

### `GET /api/v1/categories/{category_id}`

- Функция: `get_category`.
- Path: `category_id: int`.
- Ответ `200` (`CategoryRead`).
- Ошибки:
  - `404 Category not found` (нет записи или чужая запись).
  - `401`.

### `PATCH /api/v1/categories/{category_id}`

- Функция: `update_category`.
- Body (`CategoryUpdate`) частичный, например:

```json
{"name": "Supermarket"}
```

- Ответ `200` (`CategoryRead`).
- Ошибки: `404 Category not found`, `401`, `422`.

### `DELETE /api/v1/categories/{category_id}`

- Функция: `delete_category`.
- Ответ `204`.
- Ошибки: `404 Category not found`, `401`.

## 4) Tags (`app/api/routes/tags.py`)

### `GET /api/v1/tags`

- Функция: `list_tags`.
- Ответ `200` (`list[TagRead]`) для текущего пользователя.

### `POST /api/v1/tags`

- Функция: `create_tag`.
- Body (`TagCreate`):

```json
{"name": "groceries"}
```

- Ответ `201` (`TagRead`).

### `PATCH /api/v1/tags/{tag_id}`

- Функция: `update_tag`.
- Body (`TagUpdate`):

```json
{"name": "monthly"}
```

- Ответ `200` (`TagRead`).
- Ошибки: `404 Tag not found`, `401`, `422`.

### `DELETE /api/v1/tags/{tag_id}`

- Функция: `delete_tag`.
- Ответ `204`.
- Ошибки: `404 Tag not found`, `401`.

## 5) Transactions (`app/api/routes/transactions.py`)

Роутер использует helper `_build_transaction_read`, который собирает вложенный ответ: категория + список тегов с полями связи (`importance`, `note`).

### `GET /api/v1/transactions`

- Функция: `list_transactions`.
- Ответ `200` (`list[TransactionRead]`):

```json
[
  {
    "id": 10,
    "amount": 2500,
    "description": "weekly groceries",
    "transaction_date": "2026-04-15",
    "kind": "expense",
    "category": {"id": 2, "name": "Food", "kind": "expense"},
    "tags": [
      {"id": 7, "name": "groceries", "importance": 3, "note": "weekly"}
    ]
  }
]
```

- Ошибки: `401`.

### `POST /api/v1/transactions`

- Функция: `create_transaction`.
- Body (`TransactionCreate`):

```json
{
  "amount": 120000,
  "description": "salary",
  "transaction_date": "2026-04-01",
  "kind": "income",
  "category_id": 1
}
```

- Проверка: категория должна существовать и принадлежать текущему пользователю.
- Ответ `201` (`TransactionRead`).
- Ошибки:
  - `400 Invalid category`.
  - `401`, `422`.

### `GET /api/v1/transactions/{transaction_id}`

- Функция: `get_transaction`.
- Ответ `200` (`TransactionRead`).
- Ошибки: `404 Transaction not found`, `401`.

### `PATCH /api/v1/transactions/{transaction_id}`

- Функция: `update_transaction`.
- Body (`TransactionUpdate`) частичный, например:

```json
{
  "amount": 130000,
  "description": "salary bonus"
}
```

- Если обновляется `category_id`, она тоже валидируется на принадлежность.
- Ответ `200` (`TransactionRead`).
- Ошибки: `404 Transaction not found`, `400 Invalid category`, `401`, `422`.

### `DELETE /api/v1/transactions/{transaction_id}`

- Функция: `delete_transaction`.
- Действие: сначала удаляет все `TransactionTagLink` для транзакции, потом саму транзакцию.
- Ответ `204`.
- Ошибки: `404 Transaction not found`, `401`.

### `POST /api/v1/transactions/{transaction_id}/tags`

- Функция: `attach_tag`.
- Body (`TransactionTagAttach`):

```json
{
  "tag_id": 7,
  "importance": 5,
  "note": "important recurring expense"
}
```

- Если link уже есть, обновляет `importance/note`; если нет — создает.
- Ответ `200` (`TransactionRead` с обновленным `tags`).
- Ошибки:
  - `404 Transaction not found`.
  - `404 Tag not found`.
  - `401`, `422`.

### `DELETE /api/v1/transactions/{transaction_id}/tags/{tag_id}`

- Функция: `detach_tag`.
- Ответ `200` (`TransactionRead` после удаления связи).
- Ошибки:
  - `404 Transaction not found`.
  - `404 Tag link not found`.
  - `401`.

## 6) Budgets (`app/api/routes/budgets.py`)

Роутер использует helper `_budget_read` для вложенного объекта `category`.

### `GET /api/v1/budgets`

- Функция: `list_budgets`.
- Ответ `200` (`list[BudgetRead]`).

### `POST /api/v1/budgets`

- Функция: `create_budget`.
- Body (`BudgetCreate`):

```json
{
  "category_id": 2,
  "month": "2026-04",
  "limit_amount": 30000
}
```

- Ответ `201` (`BudgetRead`).
- Ошибки: `400 Invalid category`, `401`, `422`.

### `GET /api/v1/budgets/{budget_id}`

- Функция: `get_budget`.
- Ответ `200` (`BudgetRead`).
- Ошибки: `404 Budget not found`, `404 Category not found`, `401`.

### `PATCH /api/v1/budgets/{budget_id}`

- Функция: `update_budget`.
- Body (`BudgetUpdate`), например:

```json
{"limit_amount": 35000}
```

- Ответ `200` (`BudgetRead`).
- Ошибки: `404 Budget not found`, `404 Category not found`, `401`, `422`.

### `DELETE /api/v1/budgets/{budget_id}`

- Функция: `delete_budget`.
- Ответ `204`.
- Ошибки: `404 Budget not found`, `401`.

## 7) Goals (`app/api/routes/goals.py`)

### `GET /api/v1/goals`

- Функция: `list_goals`.
- Ответ `200` (`list[GoalRead]`).

### `POST /api/v1/goals`

- Функция: `create_goal`.
- Body (`GoalCreate`):

```json
{
  "title": "Emergency Fund",
  "target_amount": 300000,
  "current_amount": 50000,
  "deadline": "2026-12-31"
}
```

- Ответ `201` (`GoalRead`), `status` по умолчанию `"active"`.
- Ошибки: `401`, `422`.

### `GET /api/v1/goals/{goal_id}`

- Функция: `get_goal`.
- Ответ `200` (`GoalRead`).
- Ошибки: `404 Goal not found`, `401`.

### `PATCH /api/v1/goals/{goal_id}`

- Функция: `update_goal`.
- Body (`GoalUpdate`), например:

```json
{
  "current_amount": 120000,
  "status": "active"
}
```

- Ответ `200` (`GoalRead`).
- Ошибки: `404 Goal not found`, `401`, `422`.

### `DELETE /api/v1/goals/{goal_id}`

- Функция: `delete_goal`.
- Ответ `204`.
- Ошибки: `404 Goal not found`, `401`.

## 8) Reports (`app/api/routes/reports.py`)

### `GET /api/v1/reports/summary?month=YYYY-MM`

- Функция: `monthly_summary`.
- Query: `month` (строка формата `YYYY-MM`; формально не валидируется regex-ом в сигнатуре, парсится функцией `_month_start`).
- Логика:
  - выбирает транзакции пользователя за месяц;
  - считает `income_total`, `expense_total`, `balance`;
  - агрегирует расходы по категориям.
- Ответ `200` (`MonthlySummaryRead`):

```json
{
  "month": "2026-04",
  "income_total": 120000,
  "expense_total": 45000,
  "balance": 75000,
  "by_category": [
    {"category_id": 2, "category_name": "Food", "spent": 12000}
  ]
}
```

- Ошибки:
  - `401` токен.
  - `500` при невалидном `month` (например, `2026-XX`) из-за `int(...)` в `_month_start`.

### `GET /api/v1/reports/budget-warnings?month=YYYY-MM`

- Функция: `budget_warnings`.
- Query: `month`.
- Логика:
  - берет бюджеты пользователя за месяц;
  - считает факт расходов по каждой budget-категории;
  - возвращает только превышенные бюджеты.
- Ответ `200` (`list[BudgetWarningRead]`):

```json
[
  {
    "budget_id": 3,
    "category_id": 2,
    "category_name": "Food",
    "month": "2026-04",
    "limit_amount": 30000,
    "spent": 35200,
    "exceeded_by": 5200
  }
]
```

- Ошибки:
  - `401` токен.
  - `500` при невалидном `month`.

## Унифицированные ошибки авторизации (источник: `app/api/deps.py` + `app/core/security.py`)

В защищенных ручках можно встретить следующие `401`-ответы:

- `Missing token`
- `Invalid token`
- `Invalid token payload`
- `Invalid token subject`
- `Invalid token signature`
- `Token expired`
- `User not found`

Это важно для клиентской интеграции: фронтенд/клиент должен обрабатывать текст `detail`, а при любом `401` уметь сбрасывать сессию и переавторизовывать пользователя.
