from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable
from urllib.parse import urlparse

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Connection, Engine

from app.config import DATABASE_URL

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

category_table = Table(
    "category",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
)

tag_table = Table(
    "tag",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
)

transaction_table = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("amount", Float, nullable=False),
    Column("description", String, nullable=False),
    Column("transaction_date", Date, nullable=False),
    Column("kind", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
    Column("category_id", Integer, ForeignKey("category.id"), nullable=False),
)

transaction_tag_link_table = Table(
    "transactiontaglink",
    metadata,
    Column("transaction_id", Integer, ForeignKey("transaction.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True),
    Column("importance", Integer, nullable=False),
    Column("note", Text, nullable=False),
)

PARSER_USERNAME = "parser_bot@example.local"
PARSER_FULL_NAME = "LR3 Parser Bot"
PARSER_PASSWORD_HASH = "lr3-parser-no-login"


@dataclass(frozen=True)
class ParsedItem:
    source_url: str
    item_url: str
    title: str
    description: str
    category: str
    amount: float
    meta: str | None = None


def create_db_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def infer_category(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.netloc or "unknown-host"
    path = parsed.path.strip("/") or "root"
    first_segment = path.split("/", 1)[0]
    return f"{hostname} / {first_segment}"[:255]


def parse_amount(value: str | None) -> float:
    if not value:
        return 1.0
    normalized = value.replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)", normalized)
    if not match:
        return 1.0
    amount = float(match.group(1))
    return amount if amount > 0 else 1.0


def save_items(items: Iterable[ParsedItem], parsed_by: str) -> int:
    rows = list(items)
    if not rows:
        return 0

    engine = create_db_engine()
    try:
        with engine.begin() as connection:
            owner_id = ensure_parser_user(connection)
            tag_id = ensure_tag(connection, owner_id, f"parsed:{parsed_by}")
            category_ids: dict[str, int] = {}

            for item in rows:
                category_id = category_ids.get(item.category)
                if category_id is None:
                    category_id = ensure_category(connection, owner_id, item.category)
                    category_ids[item.category] = category_id
                transaction_id = upsert_transaction(connection, owner_id, category_id, item, parsed_by)
                ensure_transaction_tag(connection, transaction_id, tag_id, item)
    finally:
        engine.dispose()

    return len(rows)


def ensure_parser_user(connection: Connection) -> int:
    user_id = connection.scalar(select(user_table.c.id).where(user_table.c.email == PARSER_USERNAME))
    if user_id is not None:
        return int(user_id)
    insert_stmt = (
        pg_insert(user_table)
        .values(
            email=PARSER_USERNAME,
            full_name=PARSER_FULL_NAME,
            hashed_password=PARSER_PASSWORD_HASH,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        .on_conflict_do_nothing(index_elements=[user_table.c.email])
        .returning(user_table.c.id)
    )
    inserted_id = connection.scalar(insert_stmt)
    if inserted_id is not None:
        return int(inserted_id)
    user_id = connection.scalar(select(user_table.c.id).where(user_table.c.email == PARSER_USERNAME))
    if user_id is None:
        raise RuntimeError("Could not ensure parser user")
    return int(user_id)


def ensure_category(connection: Connection, user_id: int, name: str) -> int:
    category_id = connection.scalar(
        select(category_table.c.id).where(
            category_table.c.user_id == user_id,
            category_table.c.name == name[:255],
            category_table.c.kind == "expense",
        )
    )
    if category_id is not None:
        return int(category_id)
    insert_stmt = (
        pg_insert(category_table)
        .values(name=name[:255], kind="expense", user_id=user_id)
        .on_conflict_do_nothing(index_elements=[category_table.c.user_id, category_table.c.name, category_table.c.kind])
        .returning(category_table.c.id)
    )
    inserted_id = connection.scalar(insert_stmt)
    if inserted_id is not None:
        return int(inserted_id)
    category_id = connection.scalar(
        select(category_table.c.id).where(
            category_table.c.user_id == user_id,
            category_table.c.name == name[:255],
            category_table.c.kind == "expense",
        )
    )
    if category_id is None:
        raise RuntimeError("Could not ensure category")
    return int(category_id)


def ensure_tag(connection: Connection, user_id: int, name: str) -> int:
    tag_id = connection.scalar(
        select(tag_table.c.id).where(tag_table.c.user_id == user_id, tag_table.c.name == name[:255])
    )
    if tag_id is not None:
        return int(tag_id)
    insert_stmt = (
        pg_insert(tag_table)
        .values(name=name[:255], user_id=user_id)
        .on_conflict_do_nothing(index_elements=[tag_table.c.user_id, tag_table.c.name])
        .returning(tag_table.c.id)
    )
    inserted_id = connection.scalar(insert_stmt)
    if inserted_id is not None:
        return int(inserted_id)
    tag_id = connection.scalar(
        select(tag_table.c.id).where(tag_table.c.user_id == user_id, tag_table.c.name == name[:255])
    )
    if tag_id is None:
        raise RuntimeError("Could not ensure tag")
    return int(tag_id)


def source_id(item: ParsedItem, parsed_by: str) -> str:
    return f"lr3:{parsed_by}:{item.item_url}"


def upsert_transaction(
    connection: Connection,
    user_id: int,
    category_id: int,
    item: ParsedItem,
    parsed_by: str,
) -> int:
    item_source_id = source_id(item, parsed_by)
    description = "\n".join(
        [
            "LR3 parser source: web page item",
            f"Source ID: {item_source_id}",
            f"Parser: {parsed_by}",
            f"Source page: {item.source_url}",
            f"Item URL: {item.item_url}",
            "",
            item.description,
            *(["", f"Meta: {item.meta}"] if item.meta else []),
        ]
    )
    existing_id = connection.scalar(
        select(transaction_table.c.id).where(
            transaction_table.c.user_id == user_id,
            transaction_table.c.description.like(f"%Source ID: {item_source_id}%"),
        )
    )
    values = {
        "amount": item.amount,
        "description": description[:1000],
        "transaction_date": date.today(),
        "kind": "expense",
        "user_id": user_id,
        "category_id": category_id,
    }
    if existing_id is None:
        return int(connection.execute(transaction_table.insert().values(**values)).inserted_primary_key[0])
    connection.execute(transaction_table.update().where(transaction_table.c.id == existing_id).values(**values))
    return int(existing_id)


def ensure_transaction_tag(connection: Connection, transaction_id: int, tag_id: int, item: ParsedItem) -> None:
    link = connection.scalar(
        select(transaction_tag_link_table.c.transaction_id).where(
            transaction_tag_link_table.c.transaction_id == transaction_id,
            transaction_tag_link_table.c.tag_id == tag_id,
        )
    )
    if link is not None:
        return
    connection.execute(
        pg_insert(transaction_tag_link_table)
        .values(
            transaction_id=transaction_id,
            tag_id=tag_id,
            importance=5,
            note=f"{item.title[:120]} | {item.item_url}"[:255],
        )
        .on_conflict_do_nothing(index_elements=[transaction_tag_link_table.c.transaction_id, transaction_tag_link_table.c.tag_id])
    )
