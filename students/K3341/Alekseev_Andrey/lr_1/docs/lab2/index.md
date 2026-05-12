# Лабораторная работа 2

Лабораторная работа посвящена сравнению `threading`, `multiprocessing` и `asyncio` на двух типах задач:

1. вычисление суммы чисел от `1` до `10000000000000`;
2. параллельный парсинг веб-страниц с сохранением результатов в базу данных из `lr_1`.

Исходный код лабораторной находится в [students/K3341/Alekseev_Andrey/lr_2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_2).

[Открыть реализацию](implementation.md){ .md-button .md-button--primary }
[Открыть замеры](benchmarks.md){ .md-button .md-button--primary }
[Работа с БД](database_usage.md){ .md-button }

## Что реализовано

- `threading_sum.py`, `multiprocessing_sum.py`, `async_sum.py`
- `threading_parse.py`, `multiprocessing_parse.py`, `async_parse.py`
- общий модуль запуска замеров `benchmark.py`
- документация с анализом результатов и использованием БД из первой лабораторной

## Структура проекта

```text
lr_2/
├── README.md
├── requirements.txt
├── docs/
│   └── report.md
└── lab2/
    ├── benchmark.py
    ├── config.py
    ├── db.py
    ├── parsing.py
    ├── sum_utils.py
    ├── threading_sum.py
    ├── multiprocessing_sum.py
    ├── async_sum.py
    ├── threading_parse.py
    ├── multiprocessing_parse.py
    └── async_parse.py
```

## Требования задания

- у каждой программы для вычислений есть функция `calculate_sum()`
- у каждой программы для парсинга есть функция `parse_and_save(...)`
- все реализации разбивают работу на несколько независимых подзадач
- для парсинга используется база данных из `lr_1`
- выполнены замеры времени и добавлен комментарий по результатам

## Быстрый запуск

```bash
cd students/K3341/Alekseev_Andrey/lr_2
cp .env.example .env
pip install -r requirements.txt
python -m lab2.benchmark --workers 4
```

Для сценария с БД предварительно нужно поднять PostgreSQL и миграции из `lr_1`.
