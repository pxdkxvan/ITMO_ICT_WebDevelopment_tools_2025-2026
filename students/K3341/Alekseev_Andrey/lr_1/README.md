# Лабораторная: Personal Finance API (FastAPI)

Сервис для управления личными финансами:
- доходы и расходы;
- категории и бюджеты;
- теги (many-to-many через ассоциативную сущность с дополнительными полями);
- цели накоплений;
- отчеты и предупреждения о превышении бюджета;
- регистрация/авторизация, JWT, смена пароля.

## Модель данных

Таблицы (`7`):
- `user`
- `category`
- `transaction`
- `tag`
- `transactiontaglink` (ассоциативная сущность, поля связи: `importance`, `note`)
- `budget`
- `goal`

Связи:
- One-to-many: `user -> categories/transactions/budgets/goals/tags`, `category -> transactions/budgets`
- Many-to-many: `transaction <-> tag` через `transactiontaglink`

## Практики 1.1–1.3

Реализованы в отдельных папках:
- [practices/1_1](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_1)
- [practices/1_2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_2)
- [practices/1_3](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_3)

## Итоговый отчет

- GitHub Pages: [Personal Finance API - Lab Report](https://pxdkxvan.github.io/ITMO_ICT_WebDevelopment_tools_2025-2026/)
- Исходники отчета MkDocs: [docs](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/docs)
- Финальная версия кода лабораторной: [students/K3341/Alekseev_Andrey/lr_1](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1)
- Коммит с выполненной лабораторной: [d974d0b](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/d974d0b9a5b73e41642245dd6266df6bed6f82a3)

## Запуск

1. Создать и активировать venv
2. Установить зависимости:
```bash
pip install -r requirements.txt
```
3. Поднять PostgreSQL в Docker:
```bash
docker compose up -d
```
4. Проверить/обновить `.env` (уже создан в корне проекта)
5. Применить миграции:
```bash
alembic upgrade head
```
6. Запустить сервер:
```bash
uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

## Docker Compose

Файл [docker-compose.yml](docker-compose.yml) поднимает PostgreSQL 16 и создает БД/пользователя из `.env`:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`

`Settings` читает `DATABASE_URL` из `.env` через `python-dotenv` в [app/core/config.py](app/core/config.py).

## Основные эндпоинты

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me/password`
- `GET /api/v1/users`

CRUD:
- `/api/v1/categories`
- `/api/v1/tags`
- `/api/v1/transactions`
- `/api/v1/budgets`
- `/api/v1/goals`

Связи many-to-many:
- `POST /api/v1/transactions/{transaction_id}/tags`
- `DELETE /api/v1/transactions/{transaction_id}/tags/{tag_id}`

Отчеты:
- `GET /api/v1/reports/summary?month=YYYY-MM`
- `GET /api/v1/reports/budget-warnings?month=YYYY-MM`
