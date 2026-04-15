# Финальный отчет по лабораторной работе

Отчет подготовлен в формате `github-pages` (MkDocs) и содержит финальную версию реализации.

## 1. Реализованные эндпоинты

Полный каталог ручек с параметрами, примерами JSON и ошибками:

- [HTTP API](03_http_api.md)

Краткий список групп эндпоинтов:

- `GET /`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PATCH /api/v1/auth/me/password`
- `GET /api/v1/users`
- CRUD:
  - `/api/v1/categories`
  - `/api/v1/tags`
  - `/api/v1/transactions`
  - `/api/v1/budgets`
  - `/api/v1/goals`
- many-to-many:
  - `POST /api/v1/transactions/{transaction_id}/tags`
  - `DELETE /api/v1/transactions/{transaction_id}/tags/{tag_id}`
- отчеты:
  - `GET /api/v1/reports/summary?month=YYYY-MM`
  - `GET /api/v1/reports/budget-warnings?month=YYYY-MM`

## 2. Реализованные модели данных

Список таблиц и связей:

- `user`
- `category`
- `transaction`
- `tag`
- `transactiontaglink` (ассоциативная сущность с полями связи: `importance`, `note`)
- `budget`
- `goal`

Подробно по полям и связям:

- [База данных и ER-диаграмма](02_database.md)
- ORM-модели: [app/models/entities.py](/home/pxdkxvan/ITMO/WEB/lab1/app/models/entities.py)

## 3. Код соединения с БД

Подключение реализовано через SQLModel/SQLAlchemy:

- [app/db/session.py](/home/pxdkxvan/ITMO/WEB/lab1/app/db/session.py)
- Конфигурация окружения: [app/core/config.py](/home/pxdkxvan/ITMO/WEB/lab1/app/core/config.py)
- Миграции Alembic:
  - [migrations/env.py](/home/pxdkxvan/ITMO/WEB/lab1/migrations/env.py)
  - [migrations/versions/0001_init_finance_schema.py](/home/pxdkxvan/ITMO/WEB/lab1/migrations/versions/0001_init_finance_schema.py)

## 4. Ссылки на практики (обязательный блок)

Ниже укажи ссылки на GitHub после пуша в свой форк:

- Практика 1.1 (папка/ветка/коммит):
  - `<PASTE_GITHUB_LINK_HERE>`
- Практика 1.2 (папка/ветка/коммит):
  - `<PASTE_GITHUB_LINK_HERE>`
- Практика 1.3 (папка/ветка/коммит):
  - `<PASTE_GITHUB_LINK_HERE>`

Локальные материалы практик в проекте:

- [practices/1_1](/home/pxdkxvan/ITMO/WEB/lab1/practices/1_1)
- [practices/1_2](/home/pxdkxvan/ITMO/WEB/lab1/practices/1_2)
- [practices/1_3](/home/pxdkxvan/ITMO/WEB/lab1/practices/1_3)

## 5. Финальная версия кода

Отчет отражает финальную версию проекта на момент сдачи:

- Точка входа API: [main.py](/home/pxdkxvan/ITMO/WEB/lab1/main.py)
- Основное приложение: [app/main.py](/home/pxdkxvan/ITMO/WEB/lab1/app/main.py)
- Роутинг API: [app/api/__init__.py](/home/pxdkxvan/ITMO/WEB/lab1/app/api/__init__.py)
- Полная документация архитектуры и сценариев:
  - [Архитектура](01_architecture.md)
  - [Бизнес-логика и сценарии](04_business_flows.md)
