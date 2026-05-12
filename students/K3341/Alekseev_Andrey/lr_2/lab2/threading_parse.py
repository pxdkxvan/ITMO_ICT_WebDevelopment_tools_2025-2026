from __future__ import annotations

import argparse
import threading
import time

from lab2.db import ensure_parser_user
from lab2.parsing import DEFAULT_URLS, chunked, parse_and_save_sync


def parse_and_save(url: str, user_id: int) -> dict[str, str | int]:
    return parse_and_save_sync(url, user_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Threading page parser")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    args = parser.parse_args()

    user_id = ensure_parser_user()
    chunks = chunked(args.urls, args.workers)
    results: list[dict[str, str | int]] = []
    lock = threading.Lock()
    threads: list[threading.Thread] = []

    def worker(urls: list[str]) -> None:
        local_results = [parse_and_save(url, user_id) for url in urls]
        with lock:
            results.extend(local_results)

    started_at = time.perf_counter()
    for urls in chunks:
        thread = threading.Thread(target=worker, args=(urls,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - started_at

    for result in results:
        print(f"{result['url']} -> {result['title']} (tag_id={result['tag_id']})")
    print(f"saved={len(results)}")
    print(f"elapsed={elapsed:.6f}s")


if __name__ == "__main__":
    main()
