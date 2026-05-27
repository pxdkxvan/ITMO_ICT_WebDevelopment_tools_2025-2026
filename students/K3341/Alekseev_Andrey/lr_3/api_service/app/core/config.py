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
    app_name: str = os.getenv("APP_NAME", "Personal Finance API LR3")
    app_version: str = os.getenv("APP_VERSION", "3.0.0")
    database_url: str = _require_env("DATABASE_URL")
    jwt_secret: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "super_secret_value"))
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "60"))


settings = Settings()

parser_service_url = os.getenv("PARSER_SERVICE_URL", "http://localhost:8003").rstrip("/")
parser_request_timeout_seconds = float(os.getenv("PARSER_REQUEST_TIMEOUT_SECONDS", "30"))
celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
