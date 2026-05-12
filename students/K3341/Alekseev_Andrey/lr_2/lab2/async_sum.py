from __future__ import annotations

import argparse
import asyncio
import time

from lab2.sum_utils import DEFAULT_LIMIT, DEFAULT_WORKERS, calculate_range_sum, expected_sum, split_range


async def calculate_sum(start: int, end: int) -> int:
    await asyncio.sleep(0)
    return calculate_range_sum(start, end)


async def run(limit: int, workers: int) -> None:
    ranges = split_range(limit, workers)
    started_at = time.perf_counter()
    partial_sums = await asyncio.gather(*(calculate_sum(start, end) for start, end in ranges))
    total = sum(partial_sums)
    elapsed = time.perf_counter() - started_at

    print(f"async total={total}")
    print(f"expected={expected_sum(limit)}")
    print(f"workers={workers}")
    print(f"elapsed={elapsed:.6f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Async sum benchmark")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    args = parser.parse_args()
    asyncio.run(run(args.limit, args.workers))


if __name__ == "__main__":
    main()
