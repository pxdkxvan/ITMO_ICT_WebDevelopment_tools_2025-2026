from __future__ import annotations

import base64
import hashlib
import os
from urllib.parse import urlsplit, urlunsplit

import psycopg2

from lab2.config import settings


def to_psycopg2_dsn(sqlalchemy_url: str) -> str:
    parts = urlsplit(sqlalchemy_url)
    scheme = parts.scheme.replace("+psycopg2", "")
    return urlunsplit((scheme, parts.netloc, parts.path, parts.query, parts.fragment))


def get_connection():
    return psycopg2.connect(to_psycopg2_dsn(settings.database_url))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def ensure_parser_user() -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO "user" (email, full_name, hashed_password, is_active, created_at)
                VALUES (%s, %s, %s, TRUE, NOW())
                ON CONFLICT (email) DO UPDATE
                SET full_name = EXCLUDED.full_name
                RETURNING id
                """,
                (
                    settings.parser_user_email,
                    settings.parser_user_name,
                    hash_password(settings.parser_user_password),
                ),
            )
            user_id = cursor.fetchone()[0]
        connection.commit()
    return user_id


def save_page_title(title: str, user_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tag (name, user_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, name) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING id
                """,
                (title, user_id),
            )
            tag_id = cursor.fetchone()[0]
        connection.commit()
    return tag_id
