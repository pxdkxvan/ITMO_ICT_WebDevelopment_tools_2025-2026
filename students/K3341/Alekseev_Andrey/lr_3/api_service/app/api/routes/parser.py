from __future__ import annotations

from typing import Any

import httpx
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.core.config import parser_request_timeout_seconds, parser_service_url
from app.tasks import celery_app, parse_url_task

router = APIRouter(prefix="/parser", tags=["parser"])


class ParseRequest(BaseModel):
    url: HttpUrl


def _parser_error(exc: Exception) -> HTTPException:
    if isinstance(exc, httpx.HTTPStatusError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Parser service returned {exc.response.status_code}: {exc.response.text}",
        )
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Parser service is unavailable: {exc}",
    )


@router.post("/parse")
def parse_url(request: ParseRequest) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=parser_request_timeout_seconds) as client:
            response = client.post(
                f"{parser_service_url}/parse",
                json={"url": str(request.url), "parsed_by": "api-http"},
            )
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _parser_error(exc) from exc


@router.post("/parse/queue", status_code=status.HTTP_202_ACCEPTED)
def enqueue_parse_url(request: ParseRequest) -> dict[str, str]:
    task = parse_url_task.delay(str(request.url))
    return {
        "task_id": task.id,
        "status": task.status,
        "message": "Parsing task accepted",
    }


@router.get("/parse/queue/{task_id}")
def get_parse_task(task_id: str) -> dict[str, Any]:
    task_result = AsyncResult(task_id, app=celery_app)
    response: dict[str, Any] = {
        "task_id": task_id,
        "status": task_result.status,
    }

    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            response["error"] = str(task_result.result)

    return response
