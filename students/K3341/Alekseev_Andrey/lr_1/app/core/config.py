import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value


@dataclass(frozen=True)
class Settings:
    app_name: str = _require_env("APP_NAME")
    app_version: str = _require_env("APP_VERSION")
    database_url: str = _require_env("DATABASE_URL")
    jwt_secret: str = _require_env("JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = int(_require_env("JWT_EXP_MINUTES"))


settings = Settings()
