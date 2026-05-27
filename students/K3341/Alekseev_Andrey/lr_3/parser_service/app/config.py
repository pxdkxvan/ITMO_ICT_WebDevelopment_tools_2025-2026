from __future__ import annotations

import os

REQUEST_TIMEOUT_SECONDS = float(os.getenv("PARSER_REQUEST_TIMEOUT_SECONDS", "30"))
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://finance_user:finance_pass@localhost:5433/finance_db_lr3",
)
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ITMO-LR3-parser-service/1.0)"}
