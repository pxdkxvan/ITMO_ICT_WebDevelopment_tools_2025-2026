# Работа с базой данных

## Какая БД используется

Lab 2 использует PostgreSQL из `lr_1`:

- БД: `finance_db`
- пользователь: `finance_user`
- URL: `postgresql+psycopg2://finance_user:finance_pass@localhost:5432/finance_db`

## Какие таблицы задействованы

Парсер не создает отдельные таблицы, а использует схему первой лабораторной:

- `user`
- `category`
- `tag`
- `transaction`
- `transactiontaglink`

## Как данные отображаются на схему `lr_1`

### Технический пользователь

Создается пользователь:

- `email = parser_bot@example.local`
- `full_name = LR2 Parser Bot`

Этот пользователь нужен, чтобы все записи Lab 2 были изолированы от пользовательских данных `lr_1`.

### Категории

Для каждого источника создается `category` с `kind='expense'`, например:

- `Books to Scrape Page 1`
- `Books to Scrape Page 2`

### Теги

Для каждого способа парсинга используется свой тег:

- `parsed:threading`
- `parsed:multiprocessing`
- `parsed:asyncio`

### Основные записи

Каждая распарсенная карточка сохраняется в `transaction`:

- `amount` берется из цены книги;
- `description` содержит `Source ID`, URL, способ парсинга и текстовое описание;
- `transaction_date` ставится текущей датой;
- `kind='expense'`.

Связь записи и способа парсинга хранится в `transactiontaglink`.

## Защита от дублей

Для одной и той же карточки строится `Source ID`:

```text
lr2:<method>:<project_url>
```

Если запись с этим `Source ID` уже есть в `description`, выполняется обновление, а не повторная вставка.

## Как подготовить БД

```bash
cd students/K3341/Alekseev_Andrey/lr_1
docker compose --env-file .env up -d
DATABASE_URL=postgresql+psycopg2://finance_user:finance_pass@localhost:5432/finance_db python -m alembic upgrade head
```

После этого можно запускать парсеры из `lr_2`.

## Как проверить данные

Подключение к контейнеру:

```bash
docker exec -it finance_postgres psql -U finance_user -d finance_db
```

Технический пользователь:

```sql
SELECT id, email, full_name
FROM "user"
WHERE email = 'parser_bot@example.local';
```

Количество записей Lab 2:

```sql
SELECT count(*)
FROM transaction
WHERE description LIKE '%LR2 parser source:%';
```

Количество записей по способам парсинга:

```sql
SELECT substring(description from 'Parser: ([^\n]+)') AS parser,
       count(*)
FROM transaction
WHERE description LIKE '%LR2 parser source:%'
GROUP BY 1
ORDER BY 1;
```

Последний проверенный результат после полного прогона:

- `threading`: 30
- `multiprocessing`: 30
- `asyncio`: 30
- всего: 90
