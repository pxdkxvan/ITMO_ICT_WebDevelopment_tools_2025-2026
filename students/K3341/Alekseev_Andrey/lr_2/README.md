# Лабораторная работа 2

Во второй лабораторной реализованы шесть программ на Python:

- три варианта вычисления суммы чисел от `1` до `10000000000000`: `threading`, `multiprocessing`, `async`;
- три варианта параллельного парсинга веб-страниц с сохранением заголовков страниц в БД из `lr_1`.

Для записи результатов парсинга используется таблица `tag` из первой лабораторной. Скрипты автоматически создают технического пользователя `lab2.parser@example.com`, после чего сохраняют заголовки страниц как теги этого пользователя.

## Структура

- `lab2/threading_sum.py`
- `lab2/multiprocessing_sum.py`
- `lab2/async_sum.py`
- `lab2/threading_parse.py`
- `lab2/multiprocessing_parse.py`
- `lab2/async_parse.py`
- `lab2/benchmark.py`
- `docs/report.md`

## Подготовка

1. Создать виртуальное окружение.
2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Скопировать переменные окружения:

```bash
cp .env.example .env
```

4. Поднять PostgreSQL и применить миграции из `lr_1`:

```bash
cd ../lr_1
docker compose up -d
alembic upgrade head
cd ../lr_2
```

## Запуск программ

### Задача 1. Сумма чисел

```bash
python -m lab2.threading_sum
python -m lab2.multiprocessing_sum
python -m lab2.async_sum
```

Опции:

- `--limit` - верхняя граница суммы;
- `--workers` - количество параллельных задач.

Пример:

```bash
python -m lab2.multiprocessing_sum --limit 10000000000000 --workers 8
```

### Задача 2. Парсинг и сохранение в БД

```bash
python -m lab2.threading_parse
python -m lab2.multiprocessing_parse
python -m lab2.async_parse
```

Опции:

- `--workers` - количество потоков, процессов или конкурентных запросов;
- `--urls` - список URL для парсинга.

Пример:

```bash
python -m lab2.async_parse --workers 6 --urls https://www.python.org/ https://fastapi.tiangolo.com/
```

## Автоматический запуск замеров

```bash
python -m lab2.benchmark --sum-limit 10000000000000 --workers 4
```

Если БД не поднята или интернет недоступен, можно проверить только первую задачу:

```bash
python -m lab2.benchmark --skip-parse
```

## Важное замечание по задаче 1

Прямой перебор всех чисел до `10^13` практически не подходит для учебного замера. Поэтому каждая подзадача считает сумму на своем диапазоне по формуле арифметической прогрессии. Это сохраняет разбиение задачи на части и позволяет корректно сравнить накладные расходы `threading`, `multiprocessing` и `async`.
