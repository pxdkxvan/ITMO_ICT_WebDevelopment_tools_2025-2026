# Лабораторная работа 2

Лабораторная работа сравнивает `threading`, `multiprocessing` и `asyncio` на двух сценариях:

1. вычисление суммы чисел от `1` до `10_000_000_000_000`;
2. параллельный парсинг HTML-страниц с сохранением результатов в PostgreSQL из `lr_1`.

Исходный код находится в [students/K3341/Alekseev_Andrey/lr_2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_2).

[Открыть реализацию](implementation.md){ .md-button .md-button--primary }
[Открыть замеры](benchmarks.md){ .md-button .md-button--primary }
[Работа с БД](database_usage.md){ .md-button }

## Что реализовано

- три реализации Task 1: `threading_sum.py`, `multiprocessing_sum.py`, `asyncio_sum.py`;
- три реализации Task 2: `threading_parse.py`, `multiprocessing_parse.py`, `asyncio_parse.py`;
- отдельные агрегаторы `task1_benchmark.py`, `task2_benchmark.py`;
- общий запуск `benchmark.py`;
- совместимость и с `python -m ...`, и с прямым запуском `python lab2/...py`.

## Что парсится

Для стабильного публичного HTML-источника используется `books.toscrape.com`:

- `https://books.toscrape.com/catalogue/page-1.html`
- `...`
- `https://books.toscrape.com/catalogue/page-6.html`

С каждой страницы берутся первые 5 карточек книг. Для каждой карточки сохраняются:

- заголовок;
- URL книги;
- цена;
- наличие;
- служебные метаданные о способе парсинга.

## Кратко о сохранении в БД

Парсинг использует базу из `lr_1`, но не создает отдельную схему. Данные сохраняются в уже существующие таблицы:

- технический пользователь в `user`;
- категории страниц в `category`;
- признак способа парсинга в `tag`;
- карточки как записи в `transaction`;
- связь записи и тега в `transactiontaglink`.

Такой вариант был выбран потому, что в `lr_1` уже есть готовая PostgreSQL-схема и миграции.

## Быстрый запуск

```bash
cd students/K3341/Alekseev_Andrey/lr_1
docker compose --env-file .env up -d
DATABASE_URL=postgresql+psycopg2://finance_user:finance_pass@localhost:5432/finance_db python -m alembic upgrade head

cd ../lr_2
pip install -r requirements.txt
python -m lab2.benchmark
```

## Последний проверенный результат

При последнем полном прогоне:

- Task 1 завершился без ошибок во всех трех реализациях;
- Task 2 завершился без ошибок во всех трех реализациях;
- в БД было записано `90` строк `transaction` с пометкой `LR2 parser source:`.
