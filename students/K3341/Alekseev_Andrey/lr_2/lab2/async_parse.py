from __future__ import annotations

import argparse
import asyncio
import time

import aiohttp

from lab2.db import ensure_parser_user
from lab2.parsing import DEFAULT_URLS, parse_and_save_async


async def parse_and_save(url: str, user_id: int, session: aiohttp.ClientSession) -> dict[str, str | int]:
    return await parse_and_save_async(session, url, user_id)


async def run(urls: list[str], workers: int) -> None:
    user_id = await asyncio.to_thread(ensure_parser_user)
    connector = aiohttp.TCPConnector(limit_per_host=workers)
    started_at = time.perf_counter()

    async with aiohttp.ClientSession(connector=connector) as session:
        results = await asyncio.gather(*(parse_and_save(url, user_id, session) for url in urls))

    elapsed = time.perf_counter() - started_at

    for result in results:
        print(f"{result['url']} -> {result['title']} (tag_id={result['tag_id']})")
    print(f"saved={len(results)}")
    print(f"elapsed={elapsed:.6f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Async page parser")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    args = parser.parse_args()
    asyncio.run(run(args.urls, args.workers))


if __name__ == "__main__":
    main()
