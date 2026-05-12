# Работа с базой данных

## Какая БД используется

Для задачи 2 используется PostgreSQL из лабораторной работы 1:

- БД: `finance_db`
- пользователь: `finance_user`
- подключение: `postgresql+psycopg2://finance_user:finance_pass@localhost:5432/finance_db`

## Куда сохраняются данные парсинга

Заголовки веб-страниц сохраняются в таблицу `tag` из первой лабораторной.

Причины выбора:

- у таблицы есть естественное поле `name` для хранения заголовка
- не нужно придумывать фиктивные денежные значения, как для `transaction`, `budget` или `goal`
- ограничение уникальности `(user_id, name)` защищает от дублей при повторных запусках

## Какой пользователь используется

Парсинг выполняется от имени технического пользователя:

- `email`: `lab2.parser@example.com`
- `full_name`: `Lab 2 Parser`

Пользователь создается через API регистрации `lr_1`, поэтому пароль хранится в виде PBKDF2-хеша, а не в открытом виде.

## Как проверить записи

Подключиться к PostgreSQL:

```bash
docker exec -it finance_postgres psql -U finance_user -d finance_db
```

Найти пользователя:

```sql
SELECT id, email, full_name
FROM "user"
WHERE email = 'lab2.parser@example.com';
```

Посмотреть сохраненные теги:

```sql
SELECT id, name, user_id
FROM tag
WHERE user_id = (
    SELECT id
    FROM "user"
    WHERE email = 'lab2.parser@example.com'
)
ORDER BY id;
```

## Команды запуска с БД

Подготовка:

```bash
cd students/K3341/Alekseev_Andrey/lr_1
cp .env.example .env
docker compose up -d
alembic upgrade head
```

Запуск парсинга:

```bash
cd ../lr_2
cp .env.example .env
python -m lab2.threading_parse
python -m lab2.multiprocessing_parse
python -m lab2.async_parse
```

## Связь с первой лабораторной

Использование таблицы `tag` показывает, что вторая лабораторная не живет отдельно, а расширяет уже созданную инфраструктуру `lr_1`: PostgreSQL, схема данных, миграции и API пользователя.
