from __future__ import annotations

import asyncio
import gzip
import zlib
from typing import Iterable
from urllib.request import Request, urlopen

import aiohttp
from bs4 import BeautifulSoup

from lab2.config import settings
from lab2.db import save_page_title

DEFAULT_URLS = [
    "https://www.python.org/",
    "https://fastapi.tiangolo.com/",
    "https://docs.aiohttp.org/en/stable/",
    "https://www.postgresql.org/",
    "https://docs.sqlalchemy.org/en/20/",
    "https://docs.python.org/3/library/asyncio.html",
]

USER_AGENT = "Mozilla/5.0 (compatible; ITMO-Lab2/1.0)"


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        title = " ".join(soup.title.string.split())
    else:
        title = "Untitled page"
    return title[:255]


def fetch_html_sync(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=settings.request_timeout) as response:
        payload = response.read()
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        charset = response.headers.get_content_charset() or "utf-8"

        if content_encoding == "gzip":
            payload = gzip.decompress(payload)
        elif content_encoding == "deflate":
            payload = zlib.decompress(payload)

        return payload.decode(charset, errors="ignore")


def parse_and_save_sync(url: str, user_id: int) -> dict[str, str | int]:
    html = fetch_html_sync(url)
    title = extract_title(html)
    tag_id = save_page_title(title, user_id)
    return {"url": url, "title": title, "tag_id": tag_id}


async def fetch_html_async(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=settings.request_timeout) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save_async(session: aiohttp.ClientSession, url: str, user_id: int) -> dict[str, str | int]:
    html = await fetch_html_async(session, url)
    title = extract_title(html)
    tag_id = await asyncio.to_thread(save_page_title, title, user_id)
    return {"url": url, "title": title, "tag_id": tag_id}


def chunked(items: Iterable[str], parts: int) -> list[list[str]]:
    items_list = list(items)
    if parts < 1:
        raise ValueError("parts must be positive")

    base_size, remainder = divmod(len(items_list), parts)
    chunks: list[list[str]] = []
    start = 0

    for index in range(parts):
        extra = 1 if index < remainder else 0
        end = start + base_size + extra
        chunk = items_list[start:end]
        if chunk:
            chunks.append(chunk)
        start = end

    return chunks
