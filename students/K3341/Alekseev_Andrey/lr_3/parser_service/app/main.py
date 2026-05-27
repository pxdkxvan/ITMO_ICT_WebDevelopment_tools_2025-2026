from __future__ import annotations

from typing import Any

import requests
import psycopg2
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl

from app.parser import parse_and_save

app = FastAPI(title="LR3 parser service")


class ParseRequest(BaseModel):
    url: HttpUrl
    parsed_by: str = "parser-service"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse")
def parse(request: ParseRequest) -> dict[str, Any]:
    try:
        return parse_and_save(str(request.url), request.parsed_by)
    except requests.HTTPError as exc:
        response = exc.response
        code = response.status_code if response is not None else status.HTTP_502_BAD_GATEWAY
        detail = response.text[:200] if response is not None else str(exc)
        raise HTTPException(status_code=code, detail=detail) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Target URL is unavailable: {exc}",
        ) from exc
    except psycopg2.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {exc}",
        ) from exc
