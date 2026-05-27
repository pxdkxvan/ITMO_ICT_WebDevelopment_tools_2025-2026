# Реализация Lab 2

## Структура

Основные файлы лабораторной:

- `lab2/common_sum.py`
- `lab2/common_parse.py`
- `lab2/threading_sum.py`
- `lab2/multiprocessing_sum.py`
- `lab2/asyncio_sum.py`
- `lab2/threading_parse.py`
- `lab2/multiprocessing_parse.py`
- `lab2/asyncio_parse.py`
- `lab2/task1_benchmark.py`
- `lab2/task2_benchmark.py`
- `lab2/benchmark.py`

## Задача 1. Вычисление суммы

Все три реализации используют одинаковую идею:

1. диапазон `1..N` делится на части функцией `make_chunks(...)`;
2. каждая часть считается независимо;
3. итоговая сумма получается как сумма частичных результатов.

### Почему не используется прямой цикл до `10^13`

Полный перебор до `10_000_000_000_000` не имеет смысла для учебного сравнения: он слишком длинный и скрывает различия между моделями параллелизма. Поэтому каждая подзадача считает сумму своего диапазона по формуле арифметической прогрессии:

```text
S = (a1 + an) * n / 2
```

### `threading_sum.py`

- создает по одному `threading.Thread` на каждый chunk;
- каждый поток вызывает `calculate_sum(start, end)`;
- частичные суммы складываются в общем списке по индексам.

### `multiprocessing_sum.py`

- создает отдельные процессы `multiprocessing.Process`;
- результаты возвращаются через `multiprocessing.Queue`;
- после `join()` все части суммируются в главном процессе.

### `asyncio_sum.py`

- для каждого диапазона создается coroutine `calculate_sum(start, end)`;
- запуск идет через `asyncio.gather(...)`;
- это оркестрация задач, а не реальный CPU-параллелизм.

## Задача 2. Параллельный парсинг

Общий сценарий одинаков для всех режимов:

1. берется список URL из `DEFAULT_URLS` в `common_parse.py`;
2. загружается HTML;
3. из HTML извлекаются карточки книг;
4. карточки сохраняются в PostgreSQL;
5. печатается итог `extracted/saved/errors`.

### Что именно парсится

Источник: `books.toscrape.com`.

С каждой страницы берутся первые 5 карточек `article.product_pod`. Для каждой карточки извлекаются:

- `title`;
- относительный/абсолютный URL книги;
- цена;
- наличие;
- рейтинг как дополнительный `meta`.

### `threading_parse.py`

- делит URL на чанки функцией `chunk_urls(...)`;
- запускает поток на каждый chunk;
- внутри потока адреса обрабатываются последовательно.

### `multiprocessing_parse.py`

- запускает процесс на каждый chunk;
- каждый процесс возвращает список результатов через `multiprocessing.Queue`;
- после завершения процессов результаты объединяются и суммируются.

### `asyncio_parse.py`

- использует `aiohttp.ClientSession`;
- запускает конкурентные HTTP-запросы через `asyncio.gather(...)`;
- синхронное сохранение в БД отправляется в `asyncio.to_thread(...)`.

## Общие модули

### `common_sum.py`

Содержит:

- `TARGET_N`;
- `DEFAULT_WORKERS`;
- `arithmetic_progression_sum(...)`;
- `make_chunks(...)`;
- `print_result(...)`;
- `write_benchmark_results(...)`.

### `common_parse.py`

Содержит:

- `DEFAULT_URLS`;
- `ProjectItem`, `ParseResult`;
- HTML-парсинг карточек;
- подключение к PostgreSQL;
- функции `ensure_parser_user`, `ensure_category`, `ensure_tag`;
- upsert логики для `transaction` и `transactiontaglink`;
- генерацию markdown/json результатов.

## Совместимость запуска

Entry-point файлы поддерживают оба сценария:

```bash
python -m lab2.task1_benchmark
python -m lab2.task2_benchmark
python -m lab2.benchmark
```

и

```bash
python lab2/task1_benchmark.py
python lab2/task2_benchmark.py
python lab2/benchmark.py
```

Это сделано через fallback-импорты для прямого запуска файлов без package context.
