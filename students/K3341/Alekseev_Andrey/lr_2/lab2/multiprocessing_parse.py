from __future__ import annotations

import argparse
import multiprocessing as mp
import time

from lab2.db import ensure_parser_user
from lab2.parsing import DEFAULT_URLS, parse_and_save_sync


def parse_and_save(url: str, user_id: int) -> dict[str, str | int]:
    return parse_and_save_sync(url, user_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multiprocessing page parser")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--urls", nargs="*", default=DEFAULT_URLS)
    args = parser.parse_args()

    user_id = ensure_parser_user()
    started_at = time.perf_counter()
    with mp.Pool(processes=args.workers) as pool:
        results = pool.starmap(parse_and_save, [(url, user_id) for url in args.urls])

    elapsed = time.perf_counter() - started_at

    for result in results:
        print(f"{result['url']} -> {result['title']} (tag_id={result['tag_id']})")
    print(f"saved={len(results)}")
    print(f"elapsed={elapsed:.6f}s")


if __name__ == "__main__":
    main()
