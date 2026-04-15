# Personal Finance API

Финальный отчет по лабораторной работе: FastAPI-сервис для управления личными финансами с PostgreSQL, SQLModel, Alembic и JWT-авторизацией.

[Открыть финальный отчет](final_report.md){ .md-button .md-button--primary }
[Код на GitHub](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1){ .md-button }

## Разделы отчета

<div class="grid cards" markdown>

-   **Финальный отчет**

    Обязательные материалы для сдачи: эндпоинты, модели, подключение к БД и ссылки на практики.

    [Перейти](final_report.md)

-   **HTTP API**

    Полный каталог реализованных ручек, параметры запросов, JSON-примеры и ошибки.

    [Перейти](03_http_api.md)

-   **База данных**

    Таблицы, связи, ограничения, миграции и ER-диаграмма.

    [Перейти](02_database.md)

-   **Архитектура**

    Слои приложения, зависимости, схемы, модели и общий поток запроса.

    [Перейти](01_architecture.md)

-   **Бизнес-сценарии**

    Регистрация, транзакции, теги, бюджеты, цели и отчеты.

    [Перейти](04_business_flows.md)

-   **Навигация по изменениям**

    Куда идти при изменении API, бизнес-логики, моделей и окружения.

    [Перейти](05_change_navigation.md)

</div>

## Статус проекта

| Блок | Состояние |
| --- | --- |
| GitHub Pages | [опубликовано](https://pxdkxvan.github.io/ITMO_ICT_WebDevelopment_tools_2025-2026/) |
| Исходники | [папка лабораторной](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_1) |
| API | FastAPI + JWT |
| БД | PostgreSQL + SQLModel + Alembic |

## Запуск документации локально

```bash
pip install -r requirements.txt
mkdocs serve
```

## Сборка

```bash
mkdocs build
```
