# Финальный отчет по лабораторной работе

Отчет подготовлен в формате `github-pages` (MkDocs) и содержит финальную версию реализации.

- GitHub Pages: [Personal Finance API - Lab Report](https://pxdkxvan.github.io/ITMO_ICT_WebDevelopment_tools_2025-2026/)
- Исходники лабораторной: [students/K3341/Alekseev_Andrey/lr_1](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1)
- Ветка сдачи: [main](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main)
- Коммит с реализацией API и отчетом: [ef984e8](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/ef984e8798b634fe960ebe7e30220012356ffa97)

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
- ORM-модели: [app/models/entities.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/app/models/entities.py)

## 3. Код соединения с БД

Подключение реализовано через SQLModel/SQLAlchemy:

- [app/db/session.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/app/db/session.py)
- Конфигурация окружения: [app/core/config.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/app/core/config.py)
- Миграции Alembic:
  - [migrations/env.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/migrations/env.py)
  - [migrations/versions/0001_init_finance_schema.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/migrations/versions/0001_init_finance_schema.py)

## 4. Ссылки на практики (обязательный блок)

Ссылки ведут на папки практик в ветке `main`; для фиксации состояния также указан общий коммит сдачи.

- Практика 1.1 (папка/ветка/коммит):
  - [папка practices/1_1](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_1)
  - [ветка main](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main)
  - [коммит ef984e8](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/ef984e8798b634fe960ebe7e30220012356ffa97)
- Практика 1.2 (папка/ветка/коммит):
  - [папка practices/1_2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_2)
  - [ветка main](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main)
  - [коммит ef984e8](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/ef984e8798b634fe960ebe7e30220012356ffa97)
- Практика 1.3 (папка/ветка/коммит):
  - [папка practices/1_3](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_3)
  - [ветка main](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main)
  - [коммит ef984e8](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/commit/ef984e8798b634fe960ebe7e30220012356ffa97)

Материалы практик в проекте:

- [practices/1_1](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_1)
- [practices/1_2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_2)
- [practices/1_3](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/practices/1_3)

## 5. Финальная версия кода

Отчет отражает финальную версию проекта на момент сдачи:

- Точка входа API: [app/main.py](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_1/app/main.py)
- Роутинг API: [app/api/routes](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1/app/api/routes)
- Полная документация архитектуры и сценариев:
  - [Архитектура](01_architecture.md)
  - [Бизнес-логика и сценарии](04_business_flows.md)
