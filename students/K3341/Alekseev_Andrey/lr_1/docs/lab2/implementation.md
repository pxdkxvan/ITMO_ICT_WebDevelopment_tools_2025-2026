# Реализация Lab 2

## Задача 1. Сумма чисел

### `threading_sum.py`

- диапазон `1..limit` разбивается функцией `split_range()`
- для каждого поддиапазона создается поток `threading.Thread`
- каждый поток вызывает `calculate_sum(start, end)`
- итоговая сумма получается как сумма частичных результатов

### `multiprocessing_sum.py`

- используется `multiprocessing.Pool`
- каждая пара `(start, end)` уходит в отдельную задачу процесса
- частичные суммы возвращаются в главный процесс через `starmap`

### `async_sum.py`

- для каждого поддиапазона создается coroutine `calculate_sum(start, end)`
- запуск выполняется через `asyncio.gather`
- этот вариант демонстрирует кооперативную модель выполнения, но не дает реального CPU-параллелизма

### Общая функция вычисления

Вместо полного цикла до `10^13` используется формула суммы арифметической прогрессии на каждом поддиапазоне:

```text
S = n * (a1 + an) / 2
```

Такое решение выбрано сознательно. Прямой перебор чисел до `10000000000000` занял бы слишком много времени и сделал бы лабораторную непрактичной для локального запуска.

## Задача 2. Параллельный парсинг

### Общий поток обработки

1. берется список URL из `DEFAULT_URLS` в `lab2/parsing.py`
2. HTML страницы загружается синхронно или асинхронно в зависимости от режима
3. из тега `<title>` извлекается заголовок страницы
4. заголовок сохраняется в БД как запись в таблице `tag`
5. результат печатается в консоль

### `threading_parse.py`

- URL-адреса делятся на равные части функцией `chunked()`
- каждая часть обрабатывается своим потоком
- поток последовательно парсит свою группу адресов и складывает результаты в общий список

### `multiprocessing_parse.py`

- используется пул процессов `multiprocessing.Pool`
- каждый URL отправляется отдельной задаче процесса
- вариант показывает, что `multiprocessing` можно использовать и для I/O, хотя это не самый естественный инструмент для сетевых запросов

### `async_parse.py`

- используется `aiohttp.ClientSession`
- все HTTP-запросы запускаются конкурентно через `asyncio.gather`
- сохранение в БД выполняется через `asyncio.to_thread(...)`, потому что доступ к PostgreSQL реализован синхронным драйвером `psycopg2`

## Использованные модули

- `threading`
- `multiprocessing`
- `asyncio`
- `aiohttp`
- `psycopg2-binary`
- `beautifulsoup4`

## Команды запуска

```bash
python -m lab2.threading_sum
python -m lab2.multiprocessing_sum
python -m lab2.async_sum

python -m lab2.threading_parse
python -m lab2.multiprocessing_parse
python -m lab2.async_parse
```

## Файлы реализации

- [README лабораторной 2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_2/README.md)
- [docs/report.md](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/K3341/Alekseev_Andrey/lr_2/docs/report.md)
- [пакет lab2](https://github.com/pxdkxvan/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/K3341/Alekseev_Andrey/lr_2/lab2)
