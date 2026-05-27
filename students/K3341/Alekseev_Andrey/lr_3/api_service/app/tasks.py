from __future__ import annotations

from typing import Any

import httpx
from celery import Celery

from app.core.config import (
    celery_broker_url,
    celery_result_backend,
    parser_request_timeout_seconds,
    parser_service_url,
)

celery_app = Celery(
    "lr3_parser_tasks",
    broker=celery_broker_url,
    backend=celery_result_backend,
)
celery_app.conf.update(
    accept_content=["json"],
    result_serializer="json",
    task_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)


@celery_app.task(name="lr3.parse_url")
def parse_url_task(url: str) -> dict[str, Any]:
    with httpx.Client(timeout=parser_request_timeout_seconds) as client:
        response = client.post(
            f"{parser_service_url}/parse",
            json={"url": url, "parsed_by": "celery"},
        )
        response.raise_for_status()
        return response.json()
