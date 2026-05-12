from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    current_dir = Path(__file__).resolve().parent.parent
    load_dotenv(current_dir / ".env")


_load_env()


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str = _get_env("DATABASE_URL")
    parser_user_email: str = _get_env("LAB2_PARSER_USER_EMAIL", "lab2.parser@example.com")
    parser_user_name: str = _get_env("LAB2_PARSER_USER_NAME", "Lab 2 Parser")
    parser_user_password: str = _get_env("LAB2_PARSER_PASSWORD", "TempLab2Pass123!")
    request_timeout: int = int(_get_env("LAB2_REQUEST_TIMEOUT", "20"))


settings = Settings()
